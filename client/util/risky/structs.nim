# Taken from the excellent NiCOFF project by @frkngksl
# Source: https://github.com/frkngksl/NiCOFF/blob/main/Structs.nim

# The bycopy pragma can be applied to an object or tuple type and instructs the compiler to pass the type by value to procs
# * means global type
# Some structs here should be exist in winim/lean but anyway, maybe someone needs such thing . Oi!
type
    #[
    typedef struct {
	    UINT16 Machine;
	    UINT16 NumberOfSections;
	    UINT32 TimeDateStamp;
	    UINT32 PointerToSymbolTable;
	    UINT32 NumberOfSymbols;
	    UINT16 SizeOfOptionalHeader;
	    UINT16 Characteristics;
        } FileHeader;
    ]#    
    FileHeader* {.bycopy,packed.} = object
        Machine*: uint16
        NumberOfSections*: uint16
        TimeDateStamp*: uint32
        PointerToSymbolTable*: uint32
        NumberOfSymbols*: uint32
        SizeOfOptionalHeader*: uint16
        Characteristics*: uint16

    #[
        typedef struct {
	        char Name[8];					//8 bytes long null-terminated string
	        UINT32 VirtualSize;				//total size of section when loaded into memory, 0 for COFF, might be different because of padding
	        UINT32 VirtualAddress;			//address of the first byte of the section before relocations are applied, should be set to 0
	        UINT32 SizeOfRawData;			//The size of the section for COFF files
	        UINT32 PointerToRawData;		//Pointer to the beginning of the section for COFF
	        UINT32 PointerToRelocations;	//File pointer to the beginning of relocation entries
	        UINT32 PointerToLinenumbers;	//The file pointer to the beginning of line-number entries for the section. T
	        UINT16 NumberOfRelocations;		//The number of relocation entries for the section. This is set to zero for executable images. 
	        UINT16 NumberOfLinenumbers;		//The number of line-number entries for the section. This value should be zero for an image because COFF debugging information is deprecated. 
	        UINT32 Characteristics;			//The flags that describe the characteristics of the section
            } SectionHeader;
    ]#
    SectionHeader* {.bycopy,packed.} = object
        Name*: array[8,char]
        VirtualSize*: uint32
        VirtualAddress*: uint32
        SizeOfRawData*: uint32
        PointerToRawData*: uint32
        PointerToRelocations*: uint32
        PointerToLinenumbers*: uint32
        NumberOfRelocations*: uint16
        NumberOfLinenumbers*: uint16
        Characteristics*: uint32

    #[
        typedef struct {
	        union {
		        char Name[8];					//8 bytes, name of the symbol, represented as a union of 3 structs
		        UINT32	value[2];				//TODO: what does this represent?!
	        } first;
	        UINT32 Value;					//meaning depends on the section number and storage class
	        UINT16 SectionNumber;			//signed int, some values have predefined meaning
	        UINT16 Type;					//
	        UINT8 StorageClass;				//
	        UINT8 NumberOfAuxSymbols;
            } SymbolTableEntry;
    ]#

    UnionFirst* {.final,union,pure.} = object
        Name*: array[8,char]
        value*: array[2,uint32]
    
   

    SymbolTableEntry* {.bycopy, packed.} = object
        First*: UnionFirst
        Value*: uint32
        SectionNumber*: uint16
        Type*: uint16
        StorageClass*: uint8
        NumberOfAuxSymbols*: uint8

    #[
        typedef struct {
	        UINT32 VirtualAddress;
	        UINT32 SymbolTableIndex;
	        UINT16 Type;
        } RelocationTableEntry;
    ]#

    RelocationTableEntry* {.bycopy, packed.} = object
        VirtualAddress*: uint32
        SymbolTableIndex*: uint32
        Type*: uint16
    
    SectionInfo* {.bycopy.} = object
        Name*: string
        SectionOffset*: uint64
        SectionHeaderPtr*: ptr SectionHeader

    
const
    IMAGE_REL_AMD64_ABSOLUTE  =  0x0000
    IMAGE_REL_AMD64_ADDR64    =  0x0001
    IMAGE_REL_AMD64_ADDR32    =  0x0002
    IMAGE_REL_AMD64_ADDR32NB  =  0x0003
# Most common from the looks of it, just 32-bit relative address from the byte following the relocation 
    IMAGE_REL_AMD64_REL32    =   0x0004
# Second most common, 32-bit address without an image base. Not sure what that means... 
    IMAGE_REL_AMD64_REL32_1  =   0x0005
    IMAGE_REL_AMD64_REL32_2  =   0x0006
    IMAGE_REL_AMD64_REL32_3  =   0x0007
    IMAGE_REL_AMD64_REL32_4  =   0x0008
    IMAGE_REL_AMD64_REL32_5  =   0x0009
    IMAGE_REL_AMD64_SECTION  =   0x000A
    IMAGE_REL_AMD64_SECREL   =   0x000B
    IMAGE_REL_AMD64_SECREL7  =   0x000C
    IMAGE_REL_AMD64_TOKEN    =   0x000D
    IMAGE_REL_AMD64_SREL32   =   0x000E
    IMAGE_REL_AMD64_PAIR     =   0x000F
    IMAGE_REL_AMD64_SSPAN32  =   0x0010

# Storage classes.

    IMAGE_SYM_CLASS_END_OF_FUNCTION  =   cast[byte](-1)
    IMAGE_SYM_CLASS_NULL             =   0x0000
    IMAGE_SYM_CLASS_AUTOMATIC        =   0x0001
    IMAGE_SYM_CLASS_EXTERNAL         =   0x0002
    IMAGE_SYM_CLASS_STATIC           =   0x0003
    IMAGE_SYM_CLASS_REGISTER         =   0x0004
    IMAGE_SYM_CLASS_EXTERNAL_DEF     =   0x0005
    IMAGE_SYM_CLASS_LABEL            =   0x0006
    IMAGE_SYM_CLASS_UNDEFINED_LABEL  =   0x0007
    IMAGE_SYM_CLASS_MEMBER_OF_STRUCT =   0x0008
    IMAGE_SYM_CLASS_ARGUMENT         =   0x0009
    IMAGE_SYM_CLASS_STRUCT_TAG       =   0x000A
    IMAGE_SYM_CLASS_MEMBER_OF_UNION  =   0x000B
    IMAGE_SYM_CLASS_UNION_TAG        =   0x000C
    IMAGE_SYM_CLASS_TYPE_DEFINITION  =   0x000D
    IMAGE_SYM_CLASS_UNDEFINED_STATIC =   0x000E
    IMAGE_SYM_CLASS_ENUM_TAG         =   0x000F
    IMAGE_SYM_CLASS_MEMBER_OF_ENUM   =   0x0010
    IMAGE_SYM_CLASS_REGISTER_PARAM   =   0x0011
    IMAGE_SYM_CLASS_BIT_FIELD        =   0x0012
    IMAGE_SYM_CLASS_FAR_EXTERNAL     =   0x0044 
    IMAGE_SYM_CLASS_BLOCK            =   0x0064
    IMAGE_SYM_CLASS_FUNCTION         =   0x0065
    IMAGE_SYM_CLASS_END_OF_STRUCT    =   0x0066
    IMAGE_SYM_CLASS_FILE             =   0x0067
    IMAGE_SYM_CLASS_SECTION          =   0x0068
    IMAGE_SYM_CLASS_WEAK_EXTERNAL    =   0x0069
    IMAGE_SYM_CLASS_CLR_TOKEN        =   0x006B