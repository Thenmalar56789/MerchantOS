const mongoose = require("mongoose");

const purchaseIntentSchema = new mongoose.Schema(
    {
        customerMessage: {
            type: String,
            required: true
        },

        productRequested: {
            type: String
        },

        maxPrice: {
            type: Number,
            default: null
        },

        minPrice: {
            type: Number,
            default: null
        },

        requirements: {
            type: [String],
            default: []
        },

        status: {
            type: String,
            enum: [
                "created",
                "converted",
                "not_converted"
            ],
            default: "created"
        },

        convertedOrderId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Order",
            default: null
        }
    },
    {
        timestamps: true
    }
);

module.exports =
    mongoose.model(
        "PurchaseIntent",
        purchaseIntentSchema
    );