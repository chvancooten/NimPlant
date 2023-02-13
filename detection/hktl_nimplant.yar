
rule HKTL_NimPlant_Jan23_1 {
   meta:
      description = "Detects Nimplant C2 implants (simple rule)"
      author = "Florian Roth"
      reference = "https://github.com/chvancooten/NimPlant"
      date = "2023-01-30"
      score = 85
      hash1 = "3410755c6e83913c2cbf36f4e8e2475e8a9ba60dd6b8a3d25f2f1aaf7c06f0d4"
      hash2 = "b810a41c9bfb435fe237f969bfa83b245bb4a1956509761aacc4bd7ef88acea9"
      hash3 = "c9e48ba9b034e0f2043e13f950dd5b12903a4006155d6b5a456877822f9432f2"
      hash4 = "f70a3d43ae3e079ca062010e803a11d0dcc7dd2afb8466497b3e8582a70be02d"
   strings:
      $x1 = "NimPlant.dll" ascii fullword
      $x2 = "NimPlant v" ascii

      $a1 = "base64.nim" ascii fullword
      $a2 = "zippy.nim" ascii fullword
      $a3 = "whoami.nim" ascii fullword

      $sa1 = "getLocalAdm" ascii fullword 
      $sa2 = "getAv" ascii fullword
      $sa3 = "getPositionImpl" ascii fullword
   condition:
      ( 
         1 of ($x*) and 2 of ($a*)
      ) 
      or ( 
         all of ($a*) and all of ($s*) 
      )
      or 5 of them
}
