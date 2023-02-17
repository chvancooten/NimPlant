rule nimplant_detection
{
   meta:
          description = "Detects on-disk and in-memory artifacts of NimPlant C2 implants"
          author = "NVIDIA Security Team"
          date = "02/03/2023"

   strings: 
          $s1="BeaconGetSpawnTo"
          $s2="BeaconInjectProcess"
          $s3="Cannot enumerate antivirus."

          $r1=/(X\-Identifier\:\s)[a-zA-Z0-9]{8}\r\n.*NimPlant.*\r\n.*gzip/
          $r2=/(X\-Identifier\:\s)[a-zA-Z0-9]{8}\r\n.*C2 Client\r\n.*gzip/
         
            $oep = { 48 83 EC ( 28 48 8B 05 | 48 48 8B 05 ) [17] ( FC FF FF 90 90 48 83 C4 28 | C4 48 E9 91 FE FF FF 90 4C ) }
            $t1 = "parsetoml.nim" fullword
            $t2 = "zippy.nim" fullword
            $t3 = "gzip.nim" fullword
            $t4 = "deflate.nim" fullword
            $t5 = "inflate.nim" fullword

   condition:
          ( $oep and 4 of ($t*) )
          or 2 of ($s*) 
          or any of ($r*)
}