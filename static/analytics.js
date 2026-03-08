/* =========================================
ClosetFlow Analytics Engine
========================================= */

console.log("Analytics system loaded")

let categoryChart = null
let weeklyChart = null


/* =========================================
Load Analytics
========================================= */

async function loadAnalytics(){

    try{

        let res = await fetch("/api/analytics")

        let data = await res.json()

        updateStats(data)
        renderCategoryChart(data)
        renderWeeklyChart(data)
        renderMostWorn(data)
        renderLeastWorn(data)
        renderUnused(data)
        renderHeatmap(data)

    }
    catch(err){

        console.error("Analytics load error",err)

    }

}


/* =========================================
Update Stats
========================================= */

function updateStats(data){

    if(!data.wardrobe_stats) return

    document.getElementById("totalClothes").innerText =
        data.wardrobe_stats.total_clothes

    document.getElementById("outfitsWorn").innerText =
        data.wardrobe_stats.total_outfits_worn

    document.getElementById("favCategory").innerText =
        data.wardrobe_stats.favorite_category || "-"

}


/* =========================================
Category Pie Chart
========================================= */

function renderCategoryChart(data){

    let labels = Object.keys(data.category_distribution)
    let values = Object.values(data.category_distribution)

    let ctx = document.getElementById("categoryChart")

    if(categoryChart){
        categoryChart.destroy()
    }

    categoryChart = new Chart(ctx,{
        type:"pie",
        data:{
            labels:labels,
            datasets:[{
                data:values,
                backgroundColor:[
                    "#4CAF50",
                    "#2196F3",
                    "#FF9800",
                    "#9C27B0",
                    "#F44336",
                    "#00BCD4"
                ]
            }]
        },
        options:{
            plugins:{
                legend:{
                    labels:{
                        color:"white"
                    }
                }
            }
        }
    })

}


/* =========================================
Weekly Usage Line Chart
========================================= */

function renderWeeklyChart(data){

    let labels = Object.keys(data.weekly_usage)
    let values = Object.values(data.weekly_usage)

    let ctx = document.getElementById("weeklyChart")

    if(weeklyChart){
        weeklyChart.destroy()
    }

    weeklyChart = new Chart(ctx,{
        type:"line",
        data:{
            labels:labels,
            datasets:[{
                label:"Outfits Worn",
                data:values,
                borderColor:"#4CAF50",
                backgroundColor:"rgba(76,175,80,0.2)",
                fill:true,
                tension:0.3
            }]
        },
        options:{
            scales:{
                x:{
                    ticks:{color:"white"}
                },
                y:{
                    ticks:{color:"white"}
                }
            },
            plugins:{
                legend:{
                    labels:{color:"white"}
                }
            }
        }
    })

}


/* =========================================
Most Worn Items
========================================= */

function renderMostWorn(data){

    let container = document.getElementById("mostWorn")

    if(!container) return

    container.innerHTML = ""

    data.most_worn_items.forEach(item=>{

        let div = document.createElement("div")

        div.className = "list-item fade-in"

        div.innerText =
            `${item.name} (${item.wear_count} wears)`

        container.appendChild(div)

    })

}


/* =========================================
Least Worn Items
========================================= */

function renderLeastWorn(data){

    let container = document.getElementById("leastWorn")

    if(!container) return

    container.innerHTML = ""

    data.least_worn_items.forEach(item=>{

        let div = document.createElement("div")

        div.className = "list-item fade-in"

        div.innerText =
            `${item.name} (${item.wear_count} wears)`

        container.appendChild(div)

    })

}


/* =========================================
Unused Items
========================================= */

function renderUnused(data){

    let container = document.getElementById("unusedItems")

    if(!container) return

    container.innerHTML = ""

    data.not_worn_long_time.forEach(item=>{

        let div = document.createElement("div")

        div.className = "list-item fade-in"

        div.innerText =
            `${item.item.name} (${item.days_unused} days unused)`

        container.appendChild(div)

    })

}


/* =========================================
GitHub Style Heatmap
========================================= */

function renderHeatmap(data){

    let container = document.getElementById("heatmap")

    if(!container) return

    container.innerHTML = ""

    let days = Object.values(data.heatmap)

    days.forEach(v=>{

        let cell = document.createElement("div")

        cell.className = "heat-cell"

        if(v > 0){

            cell.classList.add("heat-high")

        }

        container.appendChild(cell)

    })

}


/* =========================================
Refresh Analytics
========================================= */

function refreshAnalytics(){

    loadAnalytics()

    showToast("Analytics refreshed")

}


/* =========================================
Toast Notification
========================================= */

function showToast(message){

    let toast = document.createElement("div")

    toast.innerText = message

    toast.style.position="fixed"
    toast.style.bottom="30px"
    toast.style.left="50%"
    toast.style.transform="translateX(-50%)"
    toast.style.background="#4CAF50"
    toast.style.color="white"
    toast.style.padding="10px 18px"
    toast.style.borderRadius="8px"
    toast.style.zIndex="999"

    document.body.appendChild(toast)

    setTimeout(()=>{
        toast.remove()
    },3000)

}


/* =========================================
Auto Load
========================================= */

document.addEventListener("DOMContentLoaded",()=>{

    loadAnalytics()

})