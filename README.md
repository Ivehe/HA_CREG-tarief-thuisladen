# CREG - Tarief voor terugbetaling thuisladen bedrijfswagens

This Home Assistant integration provides the "CREG-tarief" for the reimbursement of home charging for company cars (electric or plug-in hybrid).

## About

For the calculation of the reimbursement of electricity costs related to home charging of company cars, the FOD Financiën uses the so-called "CREG-tarief". 

This CREG-tarief is the monthly average commercial electricity price all-in, expressed in eurocent/kWh. An all-in price includes energy costs, network costs, levies, surcharges, and VAT for household customers, calculated per region (Flanders, Brussels, Wallonia).

More information can be found on the [CREG website](https://www.creg.be/nl/consumenten/prijzen-en-tarieven/creg-tarief-voor-terugbetaling-thuisladen-bedrijfswagens).

## Installation

### Manual Installation

1. Download this repository.
2. Copy the `custom_components/creg_tarief_thuis_laden` folder to your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

### Configuration

1. Go to **Settings** -> **Devices & Services**.
2. Click **Add Integration**.
3. Search for **CREG-tarief thuis laden**.
4. Follow the configuration flow.

## Sensors

This integration will create sensors for the reimbursement tariff per region.

## Credits

Based on the data provided by [CREG](https://www.creg.be/).
