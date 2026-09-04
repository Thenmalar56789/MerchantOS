const mongoose = require("mongoose");

const productSchema = new mongoose.Schema(
    {
        merchantId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Merchant",
            required: true
        },
        name: {
            type: String,
            required: true
        },
        category: String,
        description: String,

        price: {
            type: Number,
            required: true
        },

        costPrice: {
            type: Number,
            required: true
        },

        margin: {
            type: Number,
            required: true
        },

        inventory: {
            type: Number,
            required: true,
            default: 0
        },

        attributes: {
            type: mongoose.Schema.Types.Mixed,
            default: {}
        },

        active: {
            type: Boolean,
            default: true
        }
    },
    { timestamps: true }
);

module.exports = mongoose.model("Product", productSchema);