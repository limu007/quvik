```mermaid
flowchart
  subgraph s1[NUV Payload]
    ia[Image Acquisition]
  end
  subgraph s2[OBC]
    ip[Image PreProcessing] --> st[(Storage)] --> dl[Downlink preparation]
  end

  ia --> ip
  classDef deC fill:#00f,stroke:#000,color:#bbb;
  class ia deC;


```
