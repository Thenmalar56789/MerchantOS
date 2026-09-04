const mongoose = require("mongoose");
const path = require("path");
const dotenv = require("dotenv");

dotenv.config({
    path: path.resolve(__dirname, "../.env")
});

const Merchant = require("./models/Merchant");
const Product = require("./models/Product");
const Customer = require("./models/Customer");
const Policy = require("./models/Policy");

const seedDatabase = async () => {
    try {
        await mongoose.connect(process.env.MONGODB_URI);
        console.log("MongoDB connected");

        // Clear existing MerchantOS demo data
        await Merchant.deleteMany({});
        await Product.deleteMany({});
        await Customer.deleteMany({});
        await Policy.deleteMany({});

        // 1. Merchant
        const merchant = await Merchant.create({
            name: "GlowCare",
            category: "Skincare",
            description: "AI-ready skincare merchant",
            currency: "INR"
        });

        // 2. Products
        const products = await Product.insertMany([
            {
                merchantId: merchant._id,
                name: "GlowCare SPF 50 Sunscreen",
                category: "Sunscreen",
                description: "Lightweight SPF 50 sunscreen for oily and combination skin",
                price: 799,
                costPrice: 480,
                margin: 39.92,
                inventory: 35,
                attributes: {
                    skinType: ["oily", "combination"],
                    spf: 50,
                    size: "50ml",
                    waterResistant: true
                }
            },
            {
                merchantId: merchant._id,
                name: "GlowCare Hydrating Face Serum",
                category: "Serum",
                description: "Hyaluronic acid serum for dry and dehydrated skin",
                price: 999,
                costPrice: 580,
                margin: 41.94,
                inventory: 20,
                attributes: {
                    skinType: ["dry", "normal", "combination"],
                    ingredient: "Hyaluronic Acid",
                    size: "30ml"
                }
            },
            {
                merchantId: merchant._id,
                name: "GlowCare Oil Control Cleanser",
                category: "Cleanser",
                description: "Gentle cleanser designed for oily and acne-prone skin",
                price: 549,
                costPrice: 300,
                margin: 45.36,
                inventory: 50,
                attributes: {
                    skinType: ["oily", "acne-prone"],
                    ingredient: "Niacinamide",
                    size: "100ml"
                }
            },
            {
                merchantId: merchant._id,
                name: "GlowCare Vitamin C Serum",
                category: "Serum",
                description: "Brightening vitamin C serum",
                price: 899,
                costPrice: 700,
                margin: 22.14,
                inventory: 8,
                attributes: {
                    skinType: ["normal", "combination"],
                    ingredient: "Vitamin C",
                    size: "30ml"
                }
            },
            {
                merchantId: merchant._id,
                name: "GlowCare Daily Moisturizer",
                category: "Moisturizer",
                description: "Lightweight daily moisturizer",
                price: 699,
                costPrice: 400,
                margin: 42.78,
                inventory: 3,
                attributes: {
                    skinType: ["normal", "dry"],
                    size: "50ml"
                }
            }
        ]);

        // 3. Customers
        const customers = await Customer.insertMany([
            {
                name: "Ananya",
                email: "ananya@example.com",
                preferences: {
                    skinType: "oily",
                    concerns: ["acne", "sun protection"]
                },
                totalSpend: 2400
            },
            {
                name: "Rahul",
                email: "rahul@example.com",
                preferences: {
                    skinType: "dry",
                    concerns: ["hydration"]
                },
                totalSpend: 3200
            },
            {
                name: "Meera",
                email: "meera@example.com",
                preferences: {
                    skinType: "combination",
                    concerns: ["brightening", "sun protection"]
                },
                totalSpend: 5100
            }
        ]);

        // 4. Merchant policy
        await Policy.create({
            merchantId: merchant._id,
            minimumMarginPercent: 25,
            maximumDiscountPercent: 10,
            minimumInventory: 5,
            allowDiscounts: true,
            objective: "maximize_revenue"
        });

        console.log(`Created merchant: ${merchant.name}`);
        console.log(`Created products: ${products.length}`);
        console.log(`Created customers: ${customers.length}`);
        console.log("Created merchant policy");

        console.log("\nMerchantOS database seeded successfully!");
    } catch (error) {
        console.error("Seed failed:", error.message);
    } finally {
        await mongoose.connection.close();
    }
};

seedDatabase();