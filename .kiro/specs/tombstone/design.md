# Design

```mermaid
flowchart TD
  I["Browser desk or extension"] --> A["Restore endpoint"]
  A --> H["Normalize and check origin"]
  H --> W["Find Wayback capture"]
  W --> E["Extract numbered evidence"]
  W --> P["Return partial or missing"]
  E --> L["Render card and save locally"]
```

The archive provider is fixed. Origin connections use the resolved public address while preserving the hostname for HTTP and TLS. Only HTTP(S) and standard ports are supported. Replay body size is bounded and its content is converted to text. User-selected cards stay in browser storage. Source and date metadata remain visible on exports.
