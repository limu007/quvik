```mermaid
flowchart LR
  classDef deC fill:#55a,stroke:#000,color:#bbb;
  subgraph s1[NUV Payload]
    ia[Image Acquisition]:::deC
  end
  subgraph s2[OBC]
    ip[Image PreProcessing] ==> st[(Storage)] --> dl[Downlink preparation]
  end
  subgraph s3[FOS]
    gr[Ground reception]
  end
  subgraph s4[system PDGS]
    fits[FITS metadata revision]
  end
  subgraph s5[SOC]
    pr[Data reduction]
  end
  subgraph s0[AOCS]
    ai(Attitude information) --> ip
  end

  ia --> ip
  dl --> gr --> fits --> pr

  class ia deC;


```
