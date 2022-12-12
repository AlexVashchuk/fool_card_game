const url = '/'
const card = document.querySelector('.hand')
const button = document.querySelector('.btn')
const cards = []
let call


const behavior = function () {
    if (button.id === 'Discards' || button.id === 'Take') { call = asyncPostCall }
    if (button.id === 'Add cards') { call = makeAddons }
}

const asyncPostCall = async (payload) => {
    // document.getElementById("sortCards").setAttribute('disabled', '')
    Array.from(document.getElementsByClassName("btn")).forEach(elem => { elem.setAttribute('disabled', '') })
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Accept' : 'application/json',
                'Content-Type' : 'application/json',
                },
            body: JSON.stringify({"data": payload})
        });
        const res = await response.json();
        // data handler here
        renderData(res)
        // document.getElementById("sortCards").removeAttribute('disabled')
    }
    catch(error) {
        // document.getElementById("sortCards").removeAttribute('disabled')
        console.log(error)
    }
    Array.from(document.getElementsByClassName("btn")).forEach(elem => { elem.removeAttribute('disabled') })
}

const makeAddons = function(card) {
    const index = cards.indexOf(card)
    if (index === -1) {
        document.getElementById(card).setAttribute("class", "chosen")
        cards.push(card)
    }
    if (index > -1) {
        document.getElementById(card).removeAttribute("class");
        cards.splice(index, 1)
    }
    console.log(cards)
}

const cardClick = function (clickedId) {
    call(clickedId)
}

const buttonClick = function (action) {
    action !== 'Add cards' && call(action) //ok

    if (action === 'Add cards') {

        if (cards.length === 0) {
            data = 'Take'
        } else {
            data = cards
        }
        asyncPostCall(JSON.stringify(cards))
    }
}

const logData = function (res) {
    console.log('##### income data ########')
    console.log('######## BEGIN ###########')
    !!res.message && console.log(res.message)
    !!res.playerCards && console.log('player', res.playerCards,     Array.isArray(res.playerCards))
    !!res.opponentCards && console.log('opponent cards qty', res.opponentCards)
    !res.clearTable && console.log('clear table = false')
    !!res.clearTable && console.log('clear table = true')
    !!res.toTable && console.log('res.toTable', res.toTable, Array.isArray(res.toTable))
    !!res.fromFront && console.log('from front = true')
    !res.fromFront && console.log('from front = false')
    !!res.lastCard && console.log('last card', res.lastCard, Array.isArray(res.lastCard))
    console.log('###### END DATA ##########')
}
  
const renderData = function (res) {

    if (res.message === 'Try again') {
        return renderMessage(res.message)}
    renderMessage(res.message)
    
    // !!('winner' in res) && endGame(res)
    console.log(res.winner)
    if ('winner' in res) { endGame(res)}


    if (Array.isArray(res.toTable) && res.toTable.length === 2) {
         renderToTable(res.toTable)} // две карты на стол

    if (typeof res.toTable === 'string' ) {

        if (res.fromFront === true) {
            res.opponentCards++ 
            renderAction(res.actionText, res.fromFront)
            clearTable(res.lenDeck)
            renderOpponent(res.opponentCards)
            renderPlayer(res.playerCards, res.lastCard)
            renderToTable([res.toTable])

        } else {

            if (!!res.clearTable) { // opponent declares discards
                clearTable(res.lenDeck)
                renderOpponent(res.opponentCards)
                renderPlayer(res.playerCards, res.lastCard)


            } else { // opponent declares takes
                renderAction(res.actionText, res.fromFront)
                renderPlayer(res.playerCards)
                renderToTable([res.lastCard])
                 //change cardclick behavior while adding cards
            }
            renderAction(res.actionText, res.fromFront)
            behavior()
        }
    }
}

const renderMessage = function (message) {
    document.getElementById('message').innerHTML = message
}

const renderAction = function (actionText, fromFront) {
    btn = document.getElementsByClassName("btn")[0]
    if (fromFront === true) {
        btn.innerText = 'Take'
        btn.id = 'Take'
        
    } else {
        if (actionText === 'Add cards') {
            btn.innerText = 'Add cards'
            btn.id = 'Add cards'
        } else {
            btn.innerText = 'Discards'
            btn.id = 'Discards'          
        }
    }
}

const clearTable = function (lenDeck) {
    const desk = document.getElementById("table");
    desk.innerHTML = '';
    if ( cards.length > 0 ) {
        cards.forEach(element => {
            document.getElementById(element).parentElement.remove()
        cards.length = 0
        })}
    
    while (document.getElementById("deck").children.length - 1 > lenDeck) {
        let docu = document.getElementById("deck")
        docu.lastChild.remove()
    }
}

const renderToTable = function (toTable) {
    
    let li;
    let image;
    let queue = ['first', 'secondComp']
    let shift = 0

    if (document.getElementById("table").children.length % 2 !== 0) {
        queue = ['first', 'firstComp']
        shift = 1
    } 
    console.log(toTable)
    toTable.forEach(element => {
        li = document.createElement("li")
        image = new Image()
        image.id = element;
        if ((toTable.indexOf(element) + shift) % 2 === 0) {
            image.setAttribute('class', queue[0])
        } else {image.setAttribute('class', queue[1])}
        image.src = "static/images/".concat(element)
        if (document.getElementById(element)) {
            document.getElementById(element).parentElement.remove()
        } else {
            document.getElementById("opponent").children[0].remove()
        }   
        document.getElementById("table").appendChild(li).appendChild(image)
    })
}

const renderPlayer = function (cards, lastCard=null) { 
    if (!!lastCard) {
        lastCard = document.getElementById(lastCard)
        lastCard !== null && lastCard.parentElement.remove()
    }

    if (cards.length > 0) {
        let li
        let image 
        cards.forEach(element => {
            if (document.getElementById(element) === null) {
                li = document.createElement("li")
                li.setAttribute("class", "cardInHand")
                image = new Image()
                image.id = element;
                image.src = "static/images/".concat(element)
                image.setAttribute("onClick", "cardClick(this.id)")
                document.getElementById("hand").appendChild(li).appendChild(image)
            }
        }) 
    }
}

const renderOpponent = function (qty) {
    
    const toRender =  qty - document.getElementById("opponent").children.length
    if (toRender > 0) {
        let li
        let image
        for (let i = 0; i !== toRender; i++) {
            li = document.createElement("li")
            li.setAttribute("class", "opp")
            image = new Image()
            image.src = "static/images/single.png"
            image.class = "shirt"
            document.getElementById("opponent").appendChild(li).appendChild(image)
        }
    }
}

const renderCardFromAddons = function (card) {
    let li;
    let image;

    li = document.createElement("li")
    image = new Image();    
    image.id = card;
    image.setAttribute('class', 'first')
    image.src = "static/images/".concat(card)
    document.getElementById("table").appendChild(li).appendChild(image)
}

const sortHand = function () {

    let li
    let image
    const inHand = []
    const grupped = { '1' : [], '2' : [], '3' : [], '4' : [] }
    const trumpId = document.getElementsByClassName("bck-grnd")[0].id
    let hand = document.getElementById('hand').children
    
    let item
    Array.from(hand).forEach(elem => {
        item = elem.children[0].id.replace('.png', "").split('-')
        item[1] =  Number(item[1])
        grupped[item[0]].push(item[1])
        document.getElementById(elem.children[0].id).parentElement.remove()
    })

    for (const suit in grupped) {
        grupped[suit].sort( (a, b) => a - b )
        if (suit !== trumpId) {
            grupped[suit].forEach(item => {
                inHand.push(suit.concat('-').concat(item.toString()).concat('.png')) 
             })
        }   
    }

    grupped[trumpId].forEach(item => {
        inHand.push(trumpId.concat('-').concat(item.toString()).concat('.png')) 
    })
    
    inHand.forEach(element => {
        li = document.createElement("li")
        li.setAttribute("class", "cardInHand")
        image = new Image()
        image.id = element
        image.src = "static/images/".concat(element)
        image.setAttribute('class', 'card')
        image.setAttribute("onClick", "cardClick(this.id)")
        document.getElementById("hand").appendChild(li).appendChild(image)
    })    
}

const newGame = function () {  
    fetch('/', {
        method: 'post',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"data" : "New game"})
    })
    .then(location.reload())
}

const endGame = function (res) {
    console.log('endGame')
    if (res.winner === 'Computer') {
        if ('playerCards' in res) {
          res.playerCards.forEach(element => {
            if (!document.getElementById(element)) {
                renderCardFromAddons(element)
                document.getElementById("opponent").children[0].remove()
            }
          })
        }
        if ('toTable' in res) {
            if (!Array.isArray(res.toTable)) { res.toTable = [res.toTable] }
            renderToTable(res.toTable)
        }
    } else {
        if ('lastCard' in res) {
            renderToTable([res.lastCard])
        } else {
            if (cards.length > 0) {
                cards.forEach(element => {
                    document.getElementById(element).parentElement.remove()
                    renderCardFromAddons(element)
                })
            }
        }
    }

    renderMessage( res.winner.concat(' wins!') )
    Array.from(document.getElementsByClassName("btn")).forEach(element =>{
        element.setAttribute('disabled', '')
    })
    if (document.getElementsByClassName("hand")[0].children.length > 0) {
        console.log('we got here')
        document.getElementsByClassName("hand")[0].children.forEach(elem => {
            elem.removeAttribute('onclick')
        })
    }
}

behavior()