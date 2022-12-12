const url = '/'
const card = document.querySelector('.hand')
const button = document.querySelector('.btn')
// const action = document.querySelector('.btn').id


let call
const cards = []

// Event listeners are already in the main.html
// card.addEventListener('click', cardClick)
// button.addEventListener('click', buttonClick)

const asyncPostCall = async (payload) => {
  // console.log(payload)
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Accept' : 'aplication/json',
        'Content-Type': 'application/json',
        },
      body: JSON.stringify({ "data": payload })
          // POST request payload
      });
      // refresh vars on html page, i guess, right?
      console.log(response)
      const res = await response.json();
      console.log(res)

      
      // renderData(res)
      // return res
  } 
  catch(error) {
    // your logic
    console.log('error')
    console.log(error.message)
  } 
}

const cardClick = function (clickedId) {
  call(clickedId)
  // console.log(clickedId)
  return clickedId
}

const buttonClick = function (choise) {  
  choise !== 'add cards' && call(choise)
  choise === 'add cards' &&  asyncPostCall(JSON.stringify(cards))
}

const makeRequest = function (card) { 
  
  const index = cards.indexOf(card)
  if (index === -1) { cards.push(card) }
  if (index > -1)  { cards.splice(index, 1) }
}

const renderData = function (res) { 
  console.log(res)
  if (res.message) {
    document.getElementById('message').innerHTML = res.message }
  if (res.card) {
    console.log(res.card)
    const ul = document.getElementById('table')
    ul.append('')
    
  }
}

if (button.id === 'discards' || button.id === 'take') { call = asyncPostCall }
if (button.id === 'add cards') { call = makeRequest }

/* <img id="{{ card }}" onclick="cardClick(this.id)" src="static/images/{{card}}" class="card"></img> */