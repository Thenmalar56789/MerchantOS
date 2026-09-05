const express = require("express");
const crypto = require("crypto");
const axios = require("axios");

const Order = require("../models/Order");
const Product = require("../models/Product");
const Customer = require("../models/Customer");
const AuditLog = require("../models/AuditLog");
const PurchaseIntent =
    require("../models/PurchaseIntent");

const router = express.Router();

router.post("/verify", async (req, res) => {
    try {
        const {
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        } = req.body;

        if (
            !razorpay_order_id ||
            !razorpay_payment_id ||
            !razorpay_signature
        ) {
            return res.status(400).json({
                success: false,
                verified: false,
                message:
                    "Payment verification data is incomplete"
            });
        }

        // ---------------------------------------------
        // Find MerchantOS order
        // ---------------------------------------------

        const order =
            await Order.findOne({
                razorpayOrderId:
                    razorpay_order_id
            });

        if (!order) {
            return res.status(404).json({
                success: false,
                verified: false,
                message:
                    "MerchantOS order not found"
            });
        }

        // ---------------------------------------------
        // Prevent duplicate processing
        // ---------------------------------------------

        if (
            order.paymentStatus ===
            "paid"
        ) {
            return res.json({
                success: true,
                verified: true,
                alreadyProcessed: true,
                message:
                    "Payment was already verified",
                orderId:
                    order._id,
                razorpayPaymentId:
                    order.razorpayPaymentId
            });
        }

        // ---------------------------------------------
        // Signature verification
        // ---------------------------------------------

        const generatedSignature =
            crypto
                .createHmac(
                    "sha256",
                    process.env
                        .RAZORPAY_KEY_SECRET
                )
                .update(
                    order.razorpayOrderId +
                    "|" +
                    razorpay_payment_id
                )
                .digest("hex");

        const isValid =
            generatedSignature ===
            razorpay_signature;

        if (!isValid) {
            order.paymentStatus =
                "failed";

            await order.save();

            return res.status(400).json({
                success: false,
                verified: false,
                message:
                    "Payment signature verification failed"
            });
        }

        // ---------------------------------------------
        // Verify payment with Razorpay
        // ---------------------------------------------

        const paymentResponse =
            await axios.get(
                `https://api.razorpay.com/v1/payments/${razorpay_payment_id}`,
                {
                    auth: {
                        username:
                            process.env
                                .RAZORPAY_KEY_ID,

                        password:
                            process.env
                                .RAZORPAY_KEY_SECRET
                    }
                }
            );

        const razorpayPayment =
            paymentResponse.data;

        console.log(
            "Razorpay payment status:",
            razorpayPayment.status
        );

        if (
            razorpayPayment.status !==
            "captured"
        ) {
            return res.status(400).json({
                success: false,
                verified: false,
                message:
                    "Payment is verified but has not been captured yet"
            });
        }

        // ---------------------------------------------
        // Verify payment amount
        // ---------------------------------------------

        const expectedAmount =
            Math.round(
                order.finalAmount * 100
            );

        if (
            razorpayPayment.amount !==
            expectedAmount
        ) {
            return res.status(400).json({
                success: false,
                verified: false,
                message:
                    "Payment amount does not match the order"
            });
        }

        // ---------------------------------------------
        // Find product
        // ---------------------------------------------

        const product =
            await Product.findById(
                order.productId
            );

        if (!product) {
            return res.status(404).json({
                success: false,
                verified: false,
                message:
                    "Product not found"
            });
        }

        // ---------------------------------------------
        // Inventory check
        // ---------------------------------------------

        if (
            product.inventory <
            order.quantity
        ) {
            return res.status(400).json({
                success: false,
                verified: false,
                message:
                    "Insufficient inventory"
            });
        }

        // ---------------------------------------------
        // Confirm order
        // ---------------------------------------------

        order.paymentStatus =
            "paid";

        order.orderStatus =
            "confirmed";

        order.razorpayPaymentId =
            razorpay_payment_id;

        await order.save();

        // ---------------------------------------------
        // Decrease inventory
        // ---------------------------------------------

        product.inventory -=
            order.quantity;

        await product.save();

        // ---------------------------------------------
        // Update customer history
        // ---------------------------------------------

        const customer =
            await Customer.findById(
                order.customerId
            );

        if (customer) {

            customer.purchaseHistory.push({
                productId:
                    order.productId,

                amount:
                    order.finalAmount,

                date:
                    new Date()
            });

            customer.totalSpend +=
                order.finalAmount;

            await customer.save();
        }

        // ---------------------------------------------
        // Convert Purchase Intent
        // ---------------------------------------------

        const purchaseIntent =
            await PurchaseIntent.findOne({
                customerMessage: {
                    $exists: true
                },

                status: {
                    $ne: "converted"
                }
            }).sort({
                createdAt: -1
            });

        if (purchaseIntent) {

            purchaseIntent.status =
                "converted";

            purchaseIntent.convertedOrderId =
                order._id;

            await purchaseIntent.save();

            console.log(
                "Purchase intent converted:",
                purchaseIntent._id.toString()
            );

        } else {

            console.log(
                "No unconverted purchase intent found"
            );
        }

        // ---------------------------------------------
        // Audit log
        // ---------------------------------------------

        await AuditLog.create({
            merchantId:
                order.merchantId,

            action:
                "payment_verified_and_order_confirmed",

            actor:
                "merchant_agent",

            details: {

                orderId:
                    order._id.toString(),

                razorpayOrderId:
                    razorpay_order_id,

                razorpayPaymentId:
                    razorpay_payment_id,

                productId:
                    order.productId.toString(),

                productName:
                    product.name,

                originalAmount:
                    order.originalAmount,

                discountAmount:
                    order.discountAmount,

                finalAmount:
                    order.finalAmount,

                aiAssisted:
                    order.aiAssisted,

                revenueAttributed:
                    order.aiAssisted
                        ? order.finalAmount
                        : 0,

                inventoryRemaining:
                    product.inventory,

                purchaseIntentConverted:
                    Boolean(
                        purchaseIntent
                    )
            }
        });

        console.log(
            "Order confirmed:",
            order._id.toString()
        );

        console.log(
            "Inventory remaining:",
            product.inventory
        );

        console.log(
            "AI-assisted revenue:",
            order.aiAssisted
                ? order.finalAmount
                : 0
        );

        return res.json({
            success: true,

            verified: true,

            message:
                "Payment verified and order confirmed",

            orderId:
                order._id,

            razorpayPaymentId:
                razorpay_payment_id,

            paymentStatus:
                order.paymentStatus,

            orderStatus:
                order.orderStatus,

            revenue:
                order.finalAmount,

            aiAssisted:
                order.aiAssisted,

            purchaseIntentConverted:
                Boolean(
                    purchaseIntent
                )
        });

    } catch (error) {

        console.error(
            "Payment verification failed:",
            error.response?.data ||
            error.message
        );

        return res.status(500).json({
            success: false,
            verified: false,
            message:
                "Payment verification failed"
        });
    }
});

module.exports = router;