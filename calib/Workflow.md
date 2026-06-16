## Software development

### Planner
```mermaid
flowchart TD
a[WPX.8.70 Management
N. Werner] --> b[WPX.2.21	Validation of Payload Design
J.Řípa]
a --> c[WPX.5.4.1 	Pipeline design
F. Münz]
a --> d[WPX.5.4.2	Scheduling algorithm and alert selection
F. Münz]
a-->e[WPX.7.70	PA/QA
PA/QA manager]

```
```mermaid
flowchart TD
a[WP4.8.70 Management
N. Werner] --> b[WP4.2.21	Validation of Payload Design
J.Řípa]
a --> c[WP4.5.4.1 	Pipeline design
F. Münz]
a --> d[WP4.5.4.2	Scheduling algorithm and alert selection
F. Münz]
a-->e[WP4.7.70	PA/QA
PA/QA manager]
a-->f[WP4.5.4.3	Science operations
Science Ops. Lead]

```


```mermaid
---
config:
  kanban:
    ticketBaseUrl: 'https://quvik.cz/browse/#TICKET#'
---
kanban
  Phase B2
    [WP1.8.70 Management]
    WP1.2.21	Validation of Payload Design
    WP1.5.4.1	Pipeline design
    WP1.5.4.2	Scheduling algorithm and alert selection
    WP1.7.70	PA/QA B2
  [Phase C]
    [WP2.8.70 Management]
    WP2.2.21	Support for Payload development and production
    WP2.5.4.1	Pipeline development@{ticket:pip_dev}
    WP2.5.4.2	Scheduling development and alert processing
    WP4.7.70	PA/QA C
  id9[Phase D]
    [WP3.8.70 Management]
    WP3.2.21	Test of Payload
    WPWP3.5.4.1	Pipeline verification and performance
    WP3.5.4.2	Scheduling testing
    WP4.7.70	PA/QA D
  id10[Phase E]
    [WP4.8.70 Management]
    WP4.2.21	Payload calibration and supervision
    WP4.5.4.1	User support and maintenance
    WP4.5.4.2	Scheduling optimization
    WP4.7.70	PA/QA E
    WP4.5.4.3	Science operations
```
