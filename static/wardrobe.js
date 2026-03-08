/* =========================================
ClosetFlow Wardrobe Manager
========================================= */

console.log("Wardrobe manager loaded");


/* =========================================
Add New Clothing Item
========================================= */

async function addCloth() {

    const name = document.getElementById("clothName").value.trim();
    const section = document.getElementById("clothSection").value;
    const color = document.getElementById("clothColor").value.trim();

    if (!name || !section) {
        alert("Please fill all required fields");
        return;
    }

    try {

        const res = await fetch("/api/clothes/add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                section: section,
                color: color
            })
        });

        const data = await res.json();

        if (data.success) {

            showToast("Clothing item added");

            clearAddForm();

            refreshWardrobe();

        }

    } catch (err) {

        console.error("Add cloth error:", err);

    }

}


/* =========================================
Delete Clothing Item
========================================= */

async function deleteCloth(clothId) {

    if (!confirm("Delete this clothing item?"))
        return;

    try {

        const res = await fetch(`/api/clothes/delete/${clothId}`, {
            method: "DELETE"
        });

        const data = await res.json();

        if (data.success) {

            showToast("Clothing item deleted");

            refreshWardrobe();

        }

    } catch (err) {

        console.error("Delete error:", err);

    }

}


/* =========================================
Toggle Worn / Unworn
========================================= */

async function toggleCloth(clothId) {

    try {

        const res = await fetch(`/api/clothes/toggle/${clothId}`, {
            method: "POST"
        });

        const data = await res.json();

        if (data.success) {

            refreshWardrobe();

        }

    } catch (err) {

        console.error("Toggle error:", err);

    }

}


/* =========================================
Modify Clothing Item
========================================= */

async function updateCloth(clothId) {

    const newName = prompt("Enter new clothing name:");

    if (!newName)
        return;

    try {

        const res = await fetch(`/api/clothes/update/${clothId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: newName
            })
        });

        const data = await res.json();

        if (data.success) {

            showToast("Clothing updated");

            refreshWardrobe();

        }

    } catch (err) {

        console.error("Update error:", err);

    }

}


/* =========================================
Refresh Wardrobe Table
========================================= */

async function refreshWardrobe() {

    try {

        const res = await fetch("/api/wardrobe");

        const clothes = await res.json();

        renderWardrobe(clothes);

    } catch (err) {

        console.error("Wardrobe refresh error:", err);

    }

}


/* =========================================
Render Wardrobe Table
========================================= */

function renderWardrobe(clothes) {

    const container = document.getElementById("wardrobeContainer");

    if (!container)
        return;

    container.innerHTML = "";

    const sections = {};

    /* group clothes by section */

    clothes.forEach(cloth => {

        if (!sections[cloth.section])
            sections[cloth.section] = [];

        sections[cloth.section].push(cloth);

    });


    for (const section in sections) {

        const sectionDiv = document.createElement("div");

        sectionDiv.className = "wardrobe-section";

        sectionDiv.innerHTML = `<h3>${section}</h3>`;

        const table = document.createElement("table");

        table.className = "wardrobe-table";

        table.innerHTML = `
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Color</th>
                    <th>Status</th>
                    <th>Last Worn</th>
                    <th>Wear Count</th>
                    <th>Actions</th>
                </tr>
            </thead>
        `;

        const tbody = document.createElement("tbody");

        sections[section].forEach(cloth => {

            const row = document.createElement("tr");

            const statusTag = cloth.status === "worn"
                ? `<span class="tag-worn">worn</span>`
                : `<span class="tag-unworn">unworn</span>`;

            row.innerHTML = `
                <td>${cloth.name}</td>
                <td>${cloth.color || "-"}</td>
                <td>${statusTag}</td>
                <td>${cloth.last_worn ? cloth.last_worn : "-"}</td>
                <td>${cloth.wear_count}</td>
                <td>
                    <button onclick="toggleCloth('${cloth.id}')">Toggle</button>
                    <button onclick="updateCloth('${cloth.id}')">Modify</button>
                    <button onclick="deleteCloth('${cloth.id}')">Delete</button>
                </td>
            `;

            tbody.appendChild(row);

        });

        table.appendChild(tbody);

        sectionDiv.appendChild(table);

        container.appendChild(sectionDiv);

    }

}


/* =========================================
Clear Add Form
========================================= */

function clearAddForm() {

    document.getElementById("clothName").value = "";
    document.getElementById("clothColor").value = "";
    document.getElementById("clothSection").value = "";

}


/* =========================================
Toast Notification
========================================= */

function showToast(message) {

    const toast = document.createElement("div");

    toast.className = "toast";

    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => {

        toast.remove();

    }, 2500);

}


/* =========================================
Page Initialization
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    refreshWardrobe();

});