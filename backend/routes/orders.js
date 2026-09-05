const express = require("express");
const axios = require("axios");

const Merchant = require("../models/Merchant");
const Product = require("../models/Product");
const Customer = require("../models/Customer");
const Policy = require("../models/Policy");
const Order = require("../models/Order");
const PurchaseIntent =
    require("../models/PurchaseIntent");

const router = express.Router();

router.post("/create", async (req, res) => {
    try {
        const {
            amount,
            productName,
            intentId
        } = req.body;

        if (
            !amount ||
            !productName ||
            !intentId
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "Amount, product name and intent ID are required"
            });
        }

        const requestedAmount =
            Number(amount);

        if (
            !Number.isFinite(
                requestedAmount
            ) ||
            requestedAmount < 1
        ) {
            return res.status(400).json({
                success: false,
                message: "Invalid amount"
            });
        }

        const purchaseIntent =
            await PurchaseIntent.findById(
                intentId
            );

        if (!purchaseIntent) {
            return res.status(404).json({
                success: false,
                message:
                    "Purchase intent not found"
            });
        }

        if (
            purchaseIntent.status ===
            "converted"
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "Purchase intent has already been converted"
            });
        }

        const merchant =
            await Merchant.findOne({
                name:
                    "MerchantOS Demo Store"
            });

        if (!merchant) {
            return res.status(404).json({
                success: false,
                message:
                    "Merchant not found"
            });
        }

        const escapedProductName =
            productName.replace(
                /[.*+?^${}()|[\]\\]/g,
                "\\$&"
            );

        const product =
            await Product.findOne({
                merchantId:
                    merchant._id,

                name: {
                    $regex:
                        `^${escapedProductName}$`,
                    $options: "i"
                },

                active: true
            });

        if (!product) {
            return res.status(404).json({
                success: false,
                message:
                    "Product not found"
            });
        }

        if (
            product.inventory <= 0
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "Product is out of stock"
            });
        }

        const policy =
            await Policy.findOne({
                merchantId:
                    merchant._id
            });

        if (!policy) {
            return res.status(404).json({
                success: false,
                message:
                    "Merchant policy not found"
            });
        }

        const originalAmount =
            product.price;

        const discountAmount =
            originalAmount -
            requestedAmount;

        const discountPercent =
            (
                discountAmount /
                originalAmount
            ) * 100;

        if (
            discountAmount < 0
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "Payment amount cannot exceed product price"
            });
        }

        if (
            discountPercent >
            policy.maximumDiscountPercent
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "Discount exceeds merchant policy"
            });
        }

        const marginPercent =
            requestedAmount > 0
                ? (
                    (
                        requestedAmount -
                        product.costPrice
                    ) /
                    requestedAmount
                ) * 100
                : 0;

        if (
            marginPercent <
            policy.minimumMarginPercent
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "Payment amount violates minimum margin policy"
            });
        }

        if (
            purchaseIntent.productRequested &&
            !product.name
                .toLowerCase()
                .includes(
                    purchaseIntent
                        .productRequested
                        .toLowerCase()
                ) &&
            !purchaseIntent
                .productRequested
                .toLowerCase()
                .includes(
                    product.name
                        .toLowerCase()
                )
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "Product does not match purchase intent"
            });
        }

        if (
            purchaseIntent.maxPrice !== null &&
            requestedAmount >
            purchaseIntent.maxPrice
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "Payment amount exceeds customer's maximum budget"
            });
        }

        if (
            purchaseIntent.minPrice !== null &&
            requestedAmount <
            purchaseIntent.minPrice
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "Payment amount is below customer's minimum price"
            });
        }

        let customer =
            await Customer.findOne({
                email:
                    "demo.customer@merchantos.local"
            });

        if (!customer) {
            customer =
                await Customer.create({
                    name:
                        "Demo Customer",

                    email:
                        "demo.customer@merchantos.local",

                    purchaseHistory: [],

                    preferences: {},

                    totalSpend: 0
                });
        }

        const amountInPaise =
            Math.round(
                requestedAmount * 100
            );

        const receipt =
            `merchantos_${Date.now()}`;

        const razorpayResponse =
            await axios.post(
                "https://api.razorpay.com/v1/orders",
                {
                    amount:
                        amountInPaise,

                    currency:
                        "INR",

                    receipt:
                        receipt,

                    notes: {
                        product:
                            product.name,

                        merchant:
                            merchant.name,

                        source:
                            "MerchantOS AI Commerce",

                        purchaseIntentId:
                            intentId.toString()
                    }
                },
                {
                    auth: {
                        username:
                            process.env
                                .RAZORPAY_KEY_ID,

                        password:
                            process.env
                                .RAZORPAY_KEY_SECRET
                    },

                    headers: {
                        "Content-Type":
                            "application/json"
                    }
                }
            );

        const razorpayOrder =
            razorpayResponse.data;

        const merchantOrder =
            await Order.create({
                merchantId:
                    merchant._id,

                customerId:
                    customer._id,

                productId:
                    product._id,

                purchaseIntentId:
                    purchaseIntent._id,

                quantity: 1,

                originalAmount:
                    originalAmount,

                discountAmount:
                    Number(
                        discountAmount.toFixed(2)
                    ),

                finalAmount:
                    requestedAmount,

                paymentStatus:
                    "pending",

                orderStatus:
                    "created",

                razorpayOrderId:
                    razorpayOrder.id,

                aiAssisted:
                    true
            });

        console.log(
            "MerchantOS order created:",
            merchantOrder._id.toString()
        );

        console.log(
            "Razorpay order created:",
            razorpayOrder.id
        );

        console.log(
            "Purchase intent linked:",
            purchaseIntent._id.toString()
        );

        res.json({
            success: true,

            order:
                razorpayOrder,

            merchantOrder: {
                id:
                    merchantOrder._id,

                productId:
                    product._id,

                productName:
                    product.name,

                originalAmount:
                    originalAmount,

                discountAmount:
                    Number(
                        discountAmount.toFixed(2)
                    ),

                finalAmount:
                    requestedAmount,

                discountPercent:
                    Number(
                        discountPercent.toFixed(2)
                    ),

                intentId:
                    purchaseIntent._id
            }
        });

    } catch (error) {

        console.error(
            "Razorpay/MerchantOS order creation failed:",
            error.response?.data ||
            error.message
        );

        res.status(500).json({
            success: false,
            message:
                "Failed to create order"
        });
    }
});

module.exports = router;