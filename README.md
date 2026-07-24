# Corporate Bond Analytics Dashboard

An interactive financial analytics dashboard built with Python and Streamlit. The application calculates a corporate bond's value, Macaulay duration, and modified duration based on user-provided assumptions.

## Dashboard Features

* Calculates the present value of a corporate bond
* Calculates Macaulay duration
* Calculates modified duration
* Displays period-by-period cash flow and present value calculations
* Visualizes the inverse relationship between bond prices and yields
* Identifies whether the bond trades at a premium, discount, or par value
* Supports annual, semiannual, quarterly, and monthly payment frequencies

## Technologies Used

* Python
* Streamlit
* pandas
* NumPy

## Inputs

The dashboard allows users to enter:

* Annual coupon rate
* Years to maturity
* Yield to maturity
* Par value
* Coupon payment and compounding frequency

## Running the Project Locally

Clone or download the repository, navigate to the project directory, and install the required packages:

```bash
python -m pip install -r requirements.txt
```

Run the Streamlit application:

```bash
python -m streamlit run bond_dashboard.py
```

## Example Analysis

For a bond with a 4% annual coupon rate, six years to maturity, an 8% yield to maturity, a $1,000 par value, and semiannual payments, the dashboard calculates the bond's value and interest-rate sensitivity.

When the yield to maturity exceeds the coupon rate, the bond trades at a discount. When the coupon rate exceeds the yield to maturity, the bond trades at a premium.

