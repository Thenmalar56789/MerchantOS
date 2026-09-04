const mongoose = require("mongoose");

const policySchema = new mongoose.Schema(
    {
        merchantId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Merchant",
            required: true
        },

        minimumMarginPercent: {
            type: Number,
            default: 20
        },

        maximumDiscountPercent: {
            type: Number,
            default: 15
        },

        minimumInventory: {
            type: Number,
            default: 5
        },

        allowDiscounts: {
            type: Boolean,
            default: true
        },

        objective: {
            type: String,
            enum: [
                "maximize_revenue",
                "maximize_margin",
                "clear_inventory",
                "customer_retention"
            ],
            default: "maximize_revenue"
        }
    },
    { timestamps: true }
);

module.exports = mongoose.model("Policy", policySchema);