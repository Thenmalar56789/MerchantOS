const mongoose = require("mongoose");

const orderSchema = new mongoose.Schema(
    {
        merchantId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Merchant",
            required: true
        },

        customerId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Customer",
            required: true
        },

        productId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Product",
            required: true
        },

        quantity: {
            type: Number,
            default: 1
        },

        originalAmount: {
            type: Number,
            required: true
        },

        discountAmount: {
            type: Number,
            default: 0
        },

        finalAmount: {
            type: Number,
            required: true
        },

        paymentStatus: {
            type: String,
            enum: ["pending", "paid", "failed"],
            default: "pending"
        },

        orderStatus: {
            type: String,
            enum: ["created", "confirmed", "processing", "shipped", "delivered", "cancelled"],
            default: "created"
        },

        aiAssisted: {
            type: Boolean,
            default: false
        }
    },
    { timestamps: true }
);

module.exports = mongoose.model("Order", orderSchema);