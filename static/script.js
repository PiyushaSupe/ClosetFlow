/* =====================================
ClosetFlow Frontend Controller
===================================== */

console.log("ClosetFlow Script Loaded")


/* =====================================
Utility Functions
===================================== */

function showToast(message){

    let toast=document.createElement("div")

    toast.innerText=message

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


/* =====================================
Load Wardrobe
===================================== */

async function loadWardrobe(){

    try{

        let res=await fetch("/api/wardrobe")

        let clothes=await res.json()

        let grid=document.querySelector(".wardrobe-grid")

        if(!grid)return

        grid.innerHTML=""

        clothes.forEach(item=>{

            let card=document.createElement("div")

            card.className="cloth-card fade-in"

            card.innerHTML=`
            <div class="cloth-name">${item.name}</div>
            <div class="cloth-meta">${item.category} • ${item.color}</div>
            <div class="cloth-meta">Worn ${item.wear_count} times</div>
            `

            grid.appendChild(card)

        })

    }
    catch(err){

        console.error("Wardrobe load error",err)

    }

}


/* =====================================
AI Recommendation
===================================== */

async function refreshRecommendation(){

    try{

        let res=await fetch("/api/recommend")

        let data=await res.json()

        if(!data)return

        let container=document.querySelector(".recommendation")

        if(!container)return

        container.innerHTML=""

        addOutfitItem(container,data.top,"Top")
        addOutfitItem(container,data.bottom,"Bottom")

        if(data.outerwear)
        addOutfitItem(container,data.outerwear,"Outerwear")

        if(data.footwear)
        addOutfitItem(container,data.footwear,"Shoes")

        showToast("New AI outfit generated")

    }
    catch(err){

        console.error(err)

    }

}


function addOutfitItem(container,item,label){

    let card=document.createElement("div")

    card.className="outfit-card fade-in"

    card.innerHTML=`
        ${item.name}
        <span>${label}</span>
    `

    container.appendChild(card)

}


/* =====================================
Mark Outfit As Worn
===================================== */

async function markOutfitWorn(outfit){

    try{

        let weatherRes=await fetch("/api/recommend")

        let weatherData=await weatherRes.json()

        let payload={
            outfit:outfit,
            temperature:25,
            weather:"clear"
        }

        await fetch("/api/wear",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify(payload)
        })

        showToast("Outfit logged successfully")

    }
    catch(err){

        console.error(err)

    }

}


/* =====================================
AI Stylist Chat
===================================== */

async function sendChatMessage(){

    let input=document.getElementById("chatInput")

    if(!input)return

    let text=input.value.trim()

    if(!text)return

    input.value=""

    let chat=document.getElementById("chatMessages")

    appendChat("You",text)

    try{

        let res=await fetch("/api/stylist",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                message:text
            })
        })

        let data=await res.json()

        appendChat("AI",data.reply)

        if(data.outfit){

            appendChat("AI","Suggested outfit loaded.")

            refreshRecommendation()

        }

    }
    catch(err){

        appendChat("AI","Error contacting stylist.")

    }

}


function appendChat(sender,text){

    let chat=document.getElementById("chatMessages")

    if(!chat)return

    let div=document.createElement("div")

    div.innerHTML=`<b>${sender}:</b> ${text}`

    chat.appendChild(div)

    chat.scrollTop=chat.scrollHeight

}


/* =====================================
Multiple Outfit Suggestions
===================================== */

async function loadMultipleOutfits(){

    try{

        let res=await fetch("/api/recommend/multiple")

        let outfits=await res.json()

        let container=document.getElementById("multipleOutfits")

        if(!container)return

        container.innerHTML=""

        outfits.forEach(o=>{

            let card=document.createElement("div")

            card.className="card fade-in"

            card.innerHTML=`
                <b>${o.top.name}</b> + ${o.bottom.name}<br>
                Score: ${o.compatibility_score}
            `

            container.appendChild(card)

        })

    }
    catch(err){

        console.error(err)

    }

}


/* =====================================
Keyboard Shortcuts
===================================== */

document.addEventListener("keydown",function(e){

    if(e.key==="Enter"){

        let input=document.getElementById("chatInput")

        if(document.activeElement===input){

            sendChatMessage()

        }

    }

})


/* =====================================
Page Initialization
===================================== */

document.addEventListener("DOMContentLoaded",()=>{

    loadWardrobe()

})