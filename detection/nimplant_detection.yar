rule nimplant_detection
{
   meta:
          description = "Detects on-disk and in-memory artifacts of NimPlant C2 implants"
          author = "NVIDIA Security Team"
          date = "02/03/2023"

   strings: 
       $oep = { 48 83 EC ( 28 48 8B 05 | 48 48 8B 05 ) [17] ( FC FF FF 90 90 48 83 C4 28 | C4 48 E9 91 FE FF FF 90 4C ) }

       $t1 = "parsetoml.nim" fullword
       $t2 = "zippy.nim" fullword
       $t3 = "gzip.nim" fullword
       $t4 = "deflate.nim" fullword
       $t5 = "inflate.nim" fullword

       $ss1 = "BeaconGetSpawnTo"
       $ss2 = "BeaconInjectProcess"
       $ss3 = "Cannot enumerate antivirus."

       $sr1 = "NimPlant" fullword
       $sr2 = "C2 Client" fullword

       $sh1 = "X-Identifier" fullword
       $sh2 = "gzip" fullword
       
   condition:
          ( $oep and 4 of ($t*) )
          or ( 1 of ($ss*) and 1 of ($sr*) ) 
          or ( 1 of ($sr*) and all of ($sh*) and 2 of ($t*) ) 
}