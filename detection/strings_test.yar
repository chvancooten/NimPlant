rule SearchStrings
{
    meta:
        description = "Searches for NimPlant-specific strings on disk or in-memory. Usage: `yara64.exe -s .\\detection\\strings_test.yar .\\client-rs\\bin\\nimplant.exe`."
    
    strings:
        $nimplant_string1 = "nimplant" nocase

        $suspicious_string1 = "dinvoke"

        $debugprint_string1 = "Kill date reached, exiting..."
        $debugprint_string2 = "Initializing client..."
        $debugprint_string3 = "Registering client..."
        $debugprint_string4 = "Changed memory protection"

        $debugprint_string_re1 = /Got command: .{,10} with args .{,50} \[guid .{,10}\]/
        $debugprint_string_re2 = /Sleeping for .{,5} seconds/

        $obfstring_string1 = "Current working directory"
        $obfstring_string2 = "Successfully changed working directory"
        $obfstring_string3 = "Error changing working directory"
        $obfstring_string4 = "Invalid number of arguments received."
        $obfstring_string5 = "Failed to protect memory"

        $obfstring_http1 = /{"i": .{,8}, "u": .{,50}, "h": .{,50}, "o": .{,50}, "p": .{,5}, "P": .{,50}, "r": .{,5}}/
        $obfstring_http2 = /{"guid": .{,8}, "result": .{,500}}/

        $config_string1a = /\[ln\][.\s\S]{,500}ua = ".{,500}"/
        $config_string1b = /\[listener\][.\s\S]{,500}userAgent = ".{,500}"/
        $config_string2 = /Could not parse .{,10} from configuration/
        $config_string3a = "sleepMask"
        $config_string3b = "killDate"

        $command_string1 = "shinject"
        $command_string2 = "screenshot"
        $command_string3 = "getLocalAdm"

        $coff_string1 = "BeaconGetSpawnTo"
        $coff_string2 = "Cannot run x64 COFF on i686 architecture"
        $coff_string3 = "This BOF expects arguments"
        $coff_string4 = "Unsupported relocation type"
        
    condition:
        any of them
}