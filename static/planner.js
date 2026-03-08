/* =========================================
ClosetFlow Planner Engine
========================================= */

console.log("Planner system initialized")


/* =========================================
Global Variables
========================================= */

let draggedItem = null

const STORAGE_KEY = "closetflow_planner"


/* =========================================
Initialize Planner
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    initDragItems()
    initDropZones()
    loadPlanner()

})


/* =========================================
Drag Setup
========================================= */

function initDragItems(){

    document.querySelectorAll(".cloth-item").forEach(item => {

        item.addEventListener("dragstart", e => {

            draggedItem = item

            e.dataTransfer.setData("text/plain", item.dataset.id)

        })

    })

}


/* =========================================
Drop Zones
========================================= */

function initDropZones(){

    document.querySelectorAll(".drop-zone").forEach(zone => {

        zone.addEventListener("dragover", e => {
            e.preventDefault()
        })

        zone.addEventListener("drop", e => {

            e.preventDefault()

            if(!draggedItem) return

            let id = draggedItem.dataset.id
            let name = draggedItem.dataset.name

            addPlannerItem(zone, id, name)

            savePlanner()

        })

    })

}


/* =========================================
Add Planner Item
========================================= */

function addPlannerItem(zone, id, name){

    let div = document.createElement("div")

    div.className = "planned-item"

    div.dataset.id = id

    div.innerHTML = `
        ${name}
        <span style="float:right;cursor:pointer;">✕</span>
    `

    div.classList.add("fade-in")

    /* Remove item */

    div.querySelector("span").onclick = () => {

        div.remove()

        savePlanner()

    }

    zone.appendChild(div)

}


/* =========================================
Save Planner
========================================= */

async function savePlanner(){

    let plan = {}

    document.querySelectorAll(".drop-zone").forEach(zone => {

        let day = zone.dataset.day
        plan[day] = []

        zone.querySelectorAll(".planned-item").forEach(item => {
            plan[day].push(item.dataset.id)
        })

    })

    try{

        let res = await fetch("/api/planner/save", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(plan)
        })

        let data = await res.json()

        if(data.success){
            alert("Planner saved successfully")
        }

    }catch(err){
        console.error(err)
    }
}


/* =========================================
Load Planner
========================================= */

async function loadPlanner(){

try{

let res=await fetch("/api/planner/load")

let plan=await res.json()

Object.keys(plan).forEach(day=>{

let zone=document.querySelector(`.drop-zone[data-day="${day}"]`)

if(!zone)return

plan[day].forEach(id=>{

let item=document.querySelector(`[data-id="${id}"]`)

if(!item)return

let div=document.createElement("div")

div.className="planned-item"

div.dataset.id=id

div.innerText=item.dataset.name

zone.appendChild(div)

})

})

}catch(err){

console.error(err)

}
}

/* =========================================
Clear Planner
========================================= */

function clearPlanner(){

    if(!confirm("Clear entire weekly planner?")) return

    document.querySelectorAll(".drop-zone").forEach(zone => {

        zone.innerHTML = ""

    })

    localStorage.removeItem(STORAGE_KEY)

}


/* =========================================
Save Planned Outfits To History
========================================= */

async function commitPlannerToHistory(){

    let plan = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}")

    if(Object.keys(plan).length === 0){

        alert("Planner is empty")

        return

    }

    for(let day in plan){

        let items = plan[day]

        if(items.length === 0) continue

        let outfit = {}

        /* Assign categories roughly */

        items.forEach(i => {

            if(!outfit.top) outfit.top = i.id
            else if(!outfit.bottom) outfit.bottom = i.id
            else if(!outfit.outerwear) outfit.outerwear = i.id
            else if(!outfit.footwear) outfit.footwear = i.id

        })

        try{

            await fetch("/api/wear",{
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({
                    outfit: outfit,
                    temperature:25,
                    weather:"planned"
                })
            })

        }
        catch(err){

            console.error("Planner commit error",err)

        }

    }

    alert("Planner outfits saved to history")

}


/* =========================================
AI Weekly Suggestion (Future Ready)
========================================= */

async function generateWeeklySuggestions(){

    try{

        let res = await fetch("/api/recommend/multiple")

        let outfits = await res.json()

        let zones = document.querySelectorAll(".drop-zone")

        zones.forEach((zone,i)=>{

            if(!outfits[i]) return

            let o = outfits[i]

            zone.innerHTML=""

            if(o.top) addPlannerItem(zone, o.top.id, o.top.name)
            if(o.bottom) addPlannerItem(zone, o.bottom.id, o.bottom.name)

        })

        savePlanner()

    }
    catch(err){

        console.error(err)

    }

}