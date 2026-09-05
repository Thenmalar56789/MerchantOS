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

        purchaseIntentId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "PurchaseIntent",
            default: null
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
            enum: [
                "created",
                "confirmed",
                "processing",
                "shipped",
                "delivered",
                "cancelled"
            ],
            default: "created"
        },

        razorpayOrderId: {
            type: String,
            unique: true,
            sparse: true
        },

        razorpayPaymentId: {
            type: String
        },

        aiAssisted: {
            type: Boolean,
            default: false
        }
    },
    {
        timestamps: true
    }
);

module.exports = mongoose.model(
    "Order",
    orderSchema
);