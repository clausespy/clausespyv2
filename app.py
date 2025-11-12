


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClauseSpy Analysis Result</title>
    <style>
        /* General Body Styles */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #121212;
            color: #EAEAEA;
            margin: 0;
            padding: 2rem;
        }

        /* Main Container */
        .container {
            max-width: 900px;
            margin: auto;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }

        /* Header */
        .header {
            text-align: left;
        }
        .header h1 {
            font-size: 2rem;
            margin: 0;
            color: #FFFFFF;
        }
        .header p {
            font-size: 1rem;
            color: #A0A0A0;
            margin-top: 0.5rem;
        }

        /* Summary Cards Section */
        .summary-deck {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }
        .summary-card {
            background-color: #1E1E1E;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #333333;
        }
        .summary-card h3 {
            margin: 0 0 0.5rem 0;
            color: #A0A0A0;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .summary-card .value {
            font-size: 1.75rem;
            font-weight: bold;
        }
        
        /* Coloring for Risk Levels */
        .risk-high { color: #FF5A5A; }
        .risk-medium { color: #FFA500; }
        .risk-low { color: #4CAF50; }
        .opportunities { color: #2E9BFF; }


        /* Risk Breakdown Section */
        .risk-breakdown {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .risk-breakdown h2 {
            font-size: 1.5rem;
            color: #FFFFFF;
            border-bottom: 1px solid #333333;
            padding-bottom: 0.5rem;
            margin-bottom: 0.5rem;
        }

        /* Individual Risk Item Card */
        .risk-item {
            background-color: #1E1E1E;
            border-left: 5px solid;
            border-radius: 8px;
            padding: 1rem 1.5rem;
            border: 1px solid #333333;
            border-left-width: 5px;
        }

        /* Colors for Risk Item Borders */
        .risk-item.high { border-left-color: #FF5A5A; }
        .risk-item.medium { border-left-color: #FFA500; }
        .risk-item.low { border-left-color: #4CAF50; }

        .risk-item h4 {
            margin: 0 0 0.5rem 0;
            font-size: 1.1rem;
            color: #FFFFFF;
        }

        .risk-item p {
            margin: 0;
            color: #A0A0A0;
            line-height: 1.5;
        }

    </style>
</head>
<body>

    <div class="container">
        <!-- Header Section -->
        <header class="header">
            <!-- Replace with dynamic filename -->
            <h1>Analysis for: Freelance_Design_Agreement.pdf</h1>
            <p>Your contract, decoded.</p>
        </header>

        <!-- Summary Cards Section -->
        <section class="summary-deck">
            <div class="summary-card">
                <h3>Overall Risk</h3>
                <!-- Use JS to set class to risk-high, risk-medium, or risk-low -->
                <p class="value risk-high">High</p>
            </div>
            <div class="summary-card">
                <h3>Plain Summary</h3>
                <p class="value risk-low">Ready to Read</p>
            </div>
            <div class="summary-card">
                <h3>Opportunities</h3>
                <!-- Replace with dynamic count -->
                <p class="value opportunities">2 Found</p>
            </div>
        </section>

        <!-- Risk Breakdown Section -->
        <section class="risk-breakdown">
            <h2>Risk Breakdown</h2>

            <!-- Dynamic Risk Item: High Risk -->
            <div class="risk-item high">
                <h4>Unlimited Liability</h4>
                <p>The clause on page 4 lacks a liability cap, exposing you to significant financial risk. This should be negotiated immediately to limit your potential liability to the contract value.</p>
            </div>

            <!-- Dynamic Risk Item: Medium Risk -->
            <div class="risk-item medium">
                <h4>Aggressive Auto-Renewal</h4>
                <p>The contract renews automatically unless you provide a 90-day notice, which is longer than the industry standard of 30 days. We recommend negotiating a shorter notice period.</p>
            </div>

            <!-- Dynamic Risk Item: Low Risk -->
            <div class="risk-item low">
                <h4>Standard Force Majeure</h4>
                <p>The force majeure clause is standard and presents no unusual risks. It appropriately covers unforeseen events that may prevent contract fulfillment.</p>
            </div>
        </section>
    </div>

</body>
</html>

