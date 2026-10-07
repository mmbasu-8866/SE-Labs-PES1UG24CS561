# Lab 3: Component Modelling & Architectural Pattern Selection

Scenario: Self-Service Coffee Kiosk.

## Deliverables
- `Coffee_Kiosk_Component_Diagram.pdf` and `.png`: UML component diagram exports.
- `Coffee_Kiosk_Component_Diagram.svg`: editable vector source.
- `Architecture_Justification.pdf` and `.docx`: one-page architecture selection, two scenario reasons, security advantage, performance benefit, components, and interfaces.
- `Architecture_Style_Analysis.pdf` and `.docx`: comparison of Layered, Microservices, and Client-Server architectures plus component/interface notes.

## Selected architecture
Layered architecture deployed as a modular local kiosk application. Touchscreen, order, and menu interactions stay local; credit-card authorization crosses an explicit payment-service boundary; a printer adapter isolates hardware details.

## Components
Touchscreen UI, Order Manager, Menu & Pricing Catalog, Payment Service, Receipt Printer Adapter, and Receipt Printer hardware. Five named ball-and-socket interfaces are drawn.
