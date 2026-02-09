"use strict";

/**
 * HW1 - Blog Submission Form JavaScript
 * Srinidhi Gowda
 * DATA-236 Distributed Systems
 */

// Store submitted posts
let submissionsArray = [];

// Q5: Closure to track submission count
// Inner function maintains access to count variable even after outer function executes
const submissionCounter = (function () {
    let count = 0;
    return function () {
        count++;
        return count;
    };
})();

// Q1a: Arrow function - validate blog content is more than 25 characters
const validateContent = () => {
    const content = document.getElementById("blogContent").value.trim();
    if (content.length <= 25) {
        alert("Blog content should be more than 25 characters");
        return false;
    }
    return true;
};

// Q1b: Arrow function - validate terms checkbox is checked
const validateTerms = () => {
    const agreedToTerms = document.getElementById("terms").checked;
    if (!agreedToTerms) {
        alert("You must agree to the terms and conditions");
        return false;
    }
    return true;
};

// Main validation - checks all required fields
const validateForm = () => {
    const title = document.getElementById("blogTitle").value.trim();
    const author = document.getElementById("authorName").value.trim();
    const email = document.getElementById("email").value.trim();
    const category = document.getElementById("category").value;

    if (title === "") {
        alert("Please enter a blog title");
        return false;
    }

    if (author === "") {
        alert("Please enter author name");
        return false;
    }

    if (email === "") {
        alert("Please enter email");
        return false;
    }

    // Basic email format check
    if (!email.includes("@") || !email.includes(".")) {
        alert("Please enter a valid email");
        return false;
    }

    // Q1a: Content length validation
    if (!validateContent()) {
        return false;
    }

    if (category === "") {
        alert("Please select a category");
        return false;
    }

    // Q1b: Terms validation
    if (!validateTerms()) {
        return false;
    }

    return true;
};

// Show success message briefly
const showSuccess = () => {
    const msgDiv = document.getElementById("successMessage");
    msgDiv.style.display = "block";
    setTimeout(() => {
        msgDiv.style.display = "none";
    }, 3000);
};

// Form submission handler
document.getElementById("blogForm").addEventListener("submit", (e) => {
    e.preventDefault();

    if (!validateForm()) {
        return;
    }

    // Build form data object
    const blogPost = {
        title: document.getElementById("blogTitle").value.trim(),
        author: document.getElementById("authorName").value.trim(),
        email: document.getElementById("email").value.trim(),
        content: document.getElementById("blogContent").value.trim(),
        category: document.getElementById("category").value,
        agreedToTerms: document.getElementById("terms").checked
    };

    // Q2: Convert to JSON and log
    const jsonString = JSON.stringify(blogPost);
    console.log("Blog JSON (stringified):");
    console.log(jsonString);

    // Parse back to object
    const parsedPost = JSON.parse(jsonString);
    console.log("Parsed back to object:");
    console.log(parsedPost);

    // Q3: Destructuring to extract title and email
    const { title, email } = parsedPost;
    console.log("Destructured values:");
    console.log("Title:", title);
    console.log("Email:", email);

    // Q4: Spread operator to add submissionDate field
    const finalPost = {
        ...parsedPost,
        id: "post-" + submissionCounter(),
        submissionDate: new Date().toISOString()
    };
    console.log("Final post with spread operator (added id and submissionDate):");
    console.log(finalPost);

    // Add to array and log
    submissionsArray.push(finalPost);
    console.log("Submissions array:");
    console.log(submissionsArray);

    // Q5: Log count using closure
    console.log("Total submissions: " + submissionsArray.length);

    showSuccess();
    document.getElementById("blogForm").reset();
});
