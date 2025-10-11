// script.js — Basic version for Personal Expense Tracker
// ------------------------------------------------------
// Provides simple client-side validation and user alerts.
// No frameworks, no extras — just pure JS for a clean experience.

document.addEventListener("DOMContentLoaded", () => {
    console.log("Basic script.js loaded successfully");

    // Handle flash messages auto-hide (optional)
    const alerts = document.querySelectorAll(".alert");
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 600);
            });
        }, 3000);
    }

    // Expense form validation
    const expenseForm = document.getElementById("expenseForm");
    if (expenseForm) {
        expenseForm.addEventListener("submit", (e) => {
            const amount = document.getElementById("amount").value.trim();
            const category = document.getElementById("category").value.trim();
            const description = document.getElementById("description").value.trim();

            if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
                e.preventDefault();
                alert("Please enter a valid amount.");
                return;
            }

            if (!category) {
                e.preventDefault();
                alert("Please select a category.");
                return;
            }

            if (!description) {
                e.preventDefault();
                alert("Please enter a short description.");
                return;
            }
        });
    }

    // Profile form validation (if you have one)
    const profileForm = document.getElementById("profileForm");
    if (profileForm) {
        profileForm.addEventListener("submit", (e) => {
            const name = document.getElementById("name").value.trim();
            const email = document.getElementById("email").value.trim();

            if (!name) {
                e.preventDefault();
                alert("Name cannot be empty.");
                return;
            }

            if (!email || !email.includes("@")) {
                e.preventDefault();
                alert("Please enter a valid email address.");
                return;
            }
        });
    }

    // Logout confirmation
    const logoutBtns = document.querySelectorAll("#logoutBtn, .logout-btn, a[href*='logout']");
    logoutBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            const confirmed = confirm("Are you sure you want to log out?");
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
});
