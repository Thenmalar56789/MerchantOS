import { useState, useEffect } from "react";
import "./index.css";

function App() {
    const [message, setMessage] = useState(
        "I need a vitamin C serum under ₹1000."
    );

    const [agentResult, setAgentResult] = useState(null);
    const [intentId, setIntentId] = useState(null);

    const [loading, setLoading] = useState(false);
    const [paymentLoading, setPaymentLoading] = useState(false);
    const [paymentResult, setPaymentResult] = useState(null);
    const [error, setError] = useState("");

    const [metrics, setMetrics] = useState(null);
    const [dashboardLoading, setDashboardLoading] = useState(true);

    const loadMetrics = async () => {
        try {
            setDashboardLoading(true);

            const response = await fetch(
                "http://localhost:5000/api/dashboard/metrics"
            );

            const data = await response.json();

            if (data.success) {
                setMetrics(data.metrics);
            }
        } catch (err) {
            console.error(
                "Dashboard error:",
                err
            );
        } finally {
            setDashboardLoading(false);
        }
    };

    useEffect(() => {
        loadMetrics();
    }, []);

    const askMerchantAgent = async () => {
        if (!message.trim()) {
            return;
        }

        setLoading(true);
        setError("");
        setPaymentResult(null);
        setAgentResult(null);
        setIntentId(null);

        try {
            const response = await fetch(
                "http://localhost:5000/api/agent/recommend",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );

            const data =
                await response.json();

            if (
                !response.ok ||
                !data.success
            ) {
                throw new Error(
                    data.message ||
                    "Merchant Agent request failed"
                );
            }

            setAgentResult(data);

            setIntentId(
                data.intentId || null
            );

            loadMetrics();

        } catch (err) {
            console.error(
                "Agent error:",
                err
            );

            setError(
                "Merchant Agent is unavailable. " +
                "Make sure the AI service is running."
            );
        } finally {
            setLoading(false);
        }
    };

    const startPayment = async () => {
        if (
            !agentResult ||
            !agentResult.canPurchase ||
            !agentResult.product ||
            !agentResult.offer ||
            !intentId
        ) {
            return;
        }

        setPaymentLoading(true);
        setPaymentResult(null);
        setError("");

        try {
            const orderResponse =
                await fetch(
                    "http://localhost:5000/api/orders/create",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                amount:
                                    agentResult
                                        .offer
                                        .finalPrice,

                                productName:
                                    agentResult
                                        .product
                                        .name,

                                intentId:
                                    intentId
                            })
                    }
                );

            const orderData =
                await orderResponse.json();

            if (
                !orderResponse.ok ||
                !orderData.success
            ) {
                throw new Error(
                    orderData.message ||
                    "Unable to create payment order"
                );
            }

            const options = {
                key:
                    "YOUR_RAZORPAY_TEST_KEY_ID",

                amount:
                    orderData.order.amount,

                currency:
                    orderData.order.currency,

                name:
                    "MerchantOS",

                description:
                    agentResult.product.name,

                order_id:
                    orderData.order.id,

                handler:
                    async function (
                        response
                    ) {
                        try {
                            const verifyResponse =
                                await fetch(
                                    "http://localhost:5000/api/payments/verify",
                                    {
                                        method:
                                            "POST",

                                        headers: {
                                            "Content-Type":
                                                "application/json"
                                        },

                                        body:
                                            JSON.stringify({
                                                razorpay_order_id:
                                                    response
                                                        .razorpay_order_id,

                                                razorpay_payment_id:
                                                    response
                                                        .razorpay_payment_id,

                                                razorpay_signature:
                                                    response
                                                        .razorpay_signature
                                            })
                                    }
                                );

                            const verifyData =
                                await verifyResponse.json();

                            if (
                                !verifyResponse.ok ||
                                !verifyData.success
                            ) {
                                throw new Error(
                                    verifyData.message ||
                                    "Payment verification failed"
                                );
                            }

                            setPaymentResult(
                                verifyData
                            );

                            setPaymentLoading(
                                false
                            );

                            await loadMetrics();

                        } catch (err) {
                            console.error(
                                "Payment verification error:",
                                err
                            );

                            setError(
                                err.message ||
                                "Payment verification failed"
                            );

                            setPaymentLoading(
                                false
                            );
                        }
                    },

                modal: {
                    ondismiss:
                        function () {
                            setPaymentLoading(
                                false
                            );
                        }
                },

                prefill: {
                    name:
                        "Demo Customer",

                    email:
                        "demo.customer@merchantos.local"
                },

                theme: {
                    color:
                        "#111827"
                }
            };

            if (!window.Razorpay) {
                throw new Error(
                    "Razorpay Checkout script is not loaded."
                );
            }

            const razorpay =
                new window.Razorpay(
                    options
                );

            razorpay.on(
                "payment.failed",
                function (response) {
                    console.error(
                        "Payment failed:",
                        response.error
                    );

                    setError(
                        response.error?.description ||
                        "Payment failed"
                    );

                    setPaymentLoading(
                        false
                    );
                }
            );

            razorpay.open();

        } catch (err) {
            console.error(
                "Checkout error:",
                err
            );

            setError(
                err.message ||
                "Unable to start payment"
            );

            setPaymentLoading(
                false
            );
        }
    };

    const formatCurrency = (
        value
    ) => {
        if (
            value === undefined ||
            value === null
        ) {
            return "₹0.00";
        }

        return `₹${Number(value).toFixed(2)}`;
    };

    const getViolations = () => {
        if (!agentResult) {
            return [];
        }

        if (
            agentResult.decision?.violations
        ) {
            return agentResult.decision.violations;
        }

        if (
            agentResult.verification?.violations
        ) {
            return agentResult.verification.violations;
        }

        if (
            agentResult.violations
        ) {
            return agentResult.violations;
        }

        return [];
    };

    const violations =
        getViolations();

    return (
        <div className="app">

            <header className="topbar">

                <div className="brand">

                    <div className="brand-mark">
                        M
                    </div>

                    <div>
                        <h1>
                            MerchantOS
                        </h1>

                        <p>
                            AI Control & Growth Layer
                        </p>
                    </div>

                </div>

                <div className="status">

                    <span className="status-dot"></span>

                    AI Commerce Active

                </div>

            </header>


            <main className="main">

                <section className="agent-section">

                    <div className="section-header">

                        <div>

                            <div className="eyebrow">
                                AI COMMERCE
                            </div>

                            <h2>
                                Merchant Agent
                            </h2>

                            <p>
                                Let an external buyer agent
                                express a natural-language
                                purchase intent.
                            </p>

                        </div>

                        <div className="agent-status">

                            <span className="status-dot"></span>

                            Agent Ready

                        </div>

                    </div>


                    <div className="intent-box">

                        <label>
                            Customer purchase intent
                        </label>

                        <textarea
                            value={message}
                            onChange={
                                (e) =>
                                    setMessage(
                                        e.target.value
                                    )
                            }
                            placeholder="Example: I need a vitamin C serum under ₹1000."
                        />

                        <button
                            className="primary-button"
                            onClick={
                                askMerchantAgent
                            }
                            disabled={
                                loading
                            }
                        >
                            {loading
                                ? "Merchant Agent is thinking..."
                                : "Ask Merchant Agent →"
                            }
                        </button>

                    </div>


                    {error && (
                        <div className="error-box">
                            {error}
                        </div>
                    )}


                    {agentResult && (

                        <div className="agent-result">

                            <div className="eyebrow">
                                MERCHANT AGENT
                            </div>


                            <div className="recommendation">

                                <div className="check-icon">
                                    ✓
                                </div>

                                <div>

                                    <h3>
                                        {
                                            agentResult
                                                .canPurchase
                                                ? "Recommendation"
                                                : "Transaction Blocked"
                                        }
                                    </h3>

                                    <p>
                                        {
                                            agentResult.response
                                        }
                                    </p>

                                </div>

                            </div>


                            {!agentResult.canPurchase &&
                                violations.length > 0 && (

                                    <div className="guardrail-box">

                                        <strong>
                                            Guardrail Reason
                                        </strong>

                                        {violations.map(
                                            (
                                                violation,
                                                index
                                            ) => (
                                                <div
                                                    key={
                                                        index
                                                    }
                                                >
                                                    •{" "}
                                                    {
                                                        violation
                                                    }
                                                </div>
                                            )
                                        )}

                                    </div>

                                )}


                            {agentResult.canPurchase &&
                                agentResult.product &&
                                agentResult.offer && (

                                    <div className="offer-card">

                                        <div>

                                            <span>
                                                Product
                                            </span>

                                            <strong>
                                                {
                                                    agentResult
                                                        .product
                                                        .name
                                                }
                                            </strong>

                                            <small>
                                                {
                                                    agentResult
                                                        .product
                                                        .brand
                                                }
                                            </small>

                                        </div>


                                        <div>

                                            <span>
                                                Original
                                            </span>

                                            <strong>
                                                {
                                                    formatCurrency(
                                                        agentResult
                                                            .offer
                                                            .originalPrice
                                                    )
                                                }
                                            </strong>

                                        </div>


                                        <div>

                                            <span>
                                                AI Offer
                                            </span>

                                            <strong>
                                                {
                                                    agentResult
                                                        .offer
                                                        .discountPercent
                                                }%
                                            </strong>

                                        </div>


                                        <div>

                                            <span>
                                                Final Price
                                            </span>

                                            <strong className="final-price">
                                                {
                                                    formatCurrency(
                                                        agentResult
                                                            .offer
                                                            .finalPrice
                                                    )
                                                }
                                            </strong>

                                        </div>

                                    </div>

                                )}


                            {agentResult.canPurchase && (

                                <button
                                    className="buy-button"
                                    onClick={
                                        startPayment
                                    }
                                    disabled={
                                        paymentLoading ||
                                        !intentId
                                    }
                                >
                                    {paymentLoading
                                        ? "Opening Razorpay..."
                                        : `Buy with Razorpay · ${formatCurrency(
                                            agentResult
                                                .offer
                                                .finalPrice
                                        )}`
                                    }
                                </button>

                            )}


                            {paymentResult && (

                                <div className="success-box">

                                    <strong>
                                        ✓ Payment verified successfully
                                    </strong>

                                    <span>
                                        Order confirmed
                                    </span>

                                    <span>
                                        Revenue:{" "}
                                        {
                                            formatCurrency(
                                                paymentResult.revenue
                                            )
                                        }
                                    </span>

                                    {paymentResult.purchaseIntentConverted && (
                                        <span>
                                            Purchase Intent converted
                                        </span>
                                    )}

                                </div>

                            )}

                        </div>

                    )}


                    <div className="signals">

                        <div>
                            <span>
                                Catalogue
                            </span>

                            <strong>
                                Verified
                            </strong>
                        </div>

                        <div>
                            <span>
                                Merchant Policy
                            </span>

                            <strong>
                                Enforced
                            </strong>
                        </div>

                        <div>
                            <span>
                                Guardrails
                            </span>

                            <strong>
                                Active
                            </strong>
                        </div>

                        <div>
                            <span>
                                Payment
                            </span>

                            <strong>
                                Razorpay Test
                            </strong>
                        </div>

                    </div>

                </section>


                <section className="dashboard">

                    <div className="dashboard-header">

                        <div>

                            <h2>
                                Merchant Growth Dashboard
                            </h2>

                            <p>
                                Monitor revenue generated
                                through AI-assisted commerce.
                            </p>

                        </div>

                        <button
                            className="refresh-button"
                            onClick={
                                loadMetrics
                            }
                        >
                            ↻ Refresh
                        </button>

                    </div>


                    {!dashboardLoading &&
                        metrics && (

                            <>

                                <div className="metric-grid">

                                    <div className="metric-card">
                                        <span>
                                            Revenue Generated
                                        </span>

                                        <strong>
                                            {
                                                formatCurrency(
                                                    metrics.revenueGenerated
                                                )
                                            }
                                        </strong>

                                        <small>
                                            Total paid revenue
                                        </small>
                                    </div>


                                    <div className="metric-card">
                                        <span>
                                            AI-Assisted Revenue
                                        </span>

                                        <strong>
                                            {
                                                formatCurrency(
                                                    metrics.aiAssistedRevenue
                                                )
                                            }
                                        </strong>

                                        <small>
                                            Revenue influenced by AI
                                        </small>
                                    </div>


                                    <div className="metric-card">
                                        <span>
                                            Estimated Profit
                                        </span>

                                        <strong>
                                            {
                                                formatCurrency(
                                                    metrics.estimatedProfit
                                                )
                                            }
                                        </strong>

                                        <small>
                                            Revenue minus product cost
                                        </small>
                                    </div>


                                    <div className="metric-card">
                                        <span>
                                            Orders
                                        </span>

                                        <strong>
                                            {
                                                metrics.totalOrders
                                            }
                                        </strong>

                                        <small>
                                            Successfully paid orders
                                        </small>
                                    </div>


                                    <div className="metric-card">
                                        <span>
                                            Average Order Value
                                        </span>

                                        <strong>
                                            {
                                                formatCurrency(
                                                    metrics.averageOrderValue
                                                )
                                            }
                                        </strong>

                                        <small>
                                            Average paid order
                                        </small>
                                    </div>


                                    <div className="metric-card">
                                        <span>
                                            Discount Given
                                        </span>

                                        <strong>
                                            {
                                                formatCurrency(
                                                    metrics.discountGiven
                                                )
                                            }
                                        </strong>

                                        <small>
                                            Total discount cost
                                        </small>
                                    </div>

                                </div>


                                <div className="activity-grid">

                                    <div className="dashboard-card">

                                        <h3>
                                            AI Agent Activity
                                        </h3>

                                        <p>
                                            Agent decisions and
                                            control signals
                                        </p>

                                        <div className="stat-row">
                                            <span>
                                                AI-assisted orders
                                            </span>

                                            <strong>
                                                {
                                                    metrics.aiAssistedOrders
                                                }
                                            </strong>
                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Agent decisions
                                            </span>

                                            <strong>
                                                {
                                                    metrics.totalAgentDecisions
                                                }
                                            </strong>
                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Blocked actions
                                            </span>

                                            <strong>
                                                {
                                                    metrics.blockedActions
                                                }
                                            </strong>
                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Escalated actions
                                            </span>

                                            <strong>
                                                {
                                                    metrics.escalatedActions
                                                }
                                            </strong>
                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Clarification requests
                                            </span>

                                            <strong>
                                                {
                                                    metrics.clarificationActions
                                                }
                                            </strong>
                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Audit events
                                            </span>

                                            <strong>
                                                {
                                                    metrics.totalAuditEvents
                                                }
                                            </strong>
                                        </div>

                                    </div>


                                    <div className="dashboard-card">

                                        <h3>
                                            Commerce Outcome
                                        </h3>

                                        <p>
                                            AI impact on merchant
                                            commerce
                                        </p>

                                        <div className="highlight-stat">

                                            <span>
                                                AI Revenue Share
                                            </span>

                                            <strong>
                                                {
                                                    metrics.revenueGenerated >
                                                    0
                                                        ? (
                                                            (
                                                                metrics.aiAssistedRevenue /
                                                                metrics.revenueGenerated
                                                            ) *
                                                            100
                                                        ).toFixed(1)
                                                        : "0.0"
                                                }%
                                            </strong>

                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Purchase Intents
                                            </span>

                                            <strong>
                                                {
                                                    metrics.purchaseIntents
                                                }
                                            </strong>
                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Converted Intents
                                            </span>

                                            <strong>
                                                {
                                                    metrics.convertedIntents
                                                }
                                            </strong>
                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Conversion Rate
                                            </span>

                                            <strong>
                                                {
                                                    metrics.conversionRate
                                                }%
                                            </strong>
                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Total Orders
                                            </span>

                                            <strong>
                                                {
                                                    metrics.totalOrders
                                                }
                                            </strong>
                                        </div>

                                        <div className="stat-row">
                                            <span>
                                                Discount Cost
                                            </span>

                                            <strong>
                                                {
                                                    formatCurrency(
                                                        metrics.discountGiven
                                                    )
                                                }
                                            </strong>
                                        </div>

                                    </div>

                                </div>

                            </>

                        )}

                </section>

            </main>

        </div>
    );
}

export default App;