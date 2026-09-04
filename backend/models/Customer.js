const mongoose = require("mongoose");

const customerSchema = new mongoose.Schema(
    {
        name: String,

        email: {
            type: String,
            required: true
        },

        purchaseHistory: {
            type: [
                {
                    productId: mongoose.Schema.Types.ObjectId,
                    amount: Number,
                    date: Date
                }
            ],
            default: []
        },

        preferences: {
            type: mongoose.Schema.Types.Mixed,
            default: {}
        },

        totalSpend: {
            type: Number,
            default: 0
        }
    },
    { timestamps: true }
);

module.exports = mongoose.model("Customer", customerSchema);