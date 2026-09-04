const mongoose = require("mongoose");

const auditLogSchema = new mongoose.Schema(
    {
        merchantId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Merchant",
            required: true
        },

        action: {
            type: String,
            required: true
        },

        actor: {
            type: String,
            enum: ["buyer_agent", "merchant_agent", "system", "merchant"],
            required: true
        },

        details: {
            type: mongoose.Schema.Types.Mixed,
            default: {}
        }
    },
    { timestamps: true }
);

module.exports = mongoose.model("AuditLog", auditLogSchema);