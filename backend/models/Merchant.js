const mongoose = require("mongoose");

const merchantSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: true
        },
        category: {
            type: String,
            required: true
        },
        description: String,
        currency: {
            type: String,
            default: "INR"
        }
    },
    { timestamps: true }
);

module.exports = mongoose.model("Merchant", merchantSchema);