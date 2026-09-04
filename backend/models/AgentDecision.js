const mongoose = require("mongoose");

const agentDecisionSchema = new mongoose.Schema(
    {
        merchantId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Merchant",
            required: true
        },

        customerId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Customer"
        },

        productId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Product"
        },

        intent: {
            type: mongoose.Schema.Types.Mixed,
            required: true
        },

        decision: {
            type: String,
            enum: [
                "recommend",
                "offer",
                "reject",
                "clarify",
                "escalate"
            ],
            required: true
        },

        reasoning: String,

        discountPercent: {
            type: Number,
            default: 0
        },

        guardrailResult: {
            type: String,
            enum: ["passed", "blocked", "modified"]
        }
    },
    { timestamps: true }
);

module.exports = mongoose.model("AgentDecision", agentDecisionSchema);