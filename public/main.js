
var url = "http://quantum-poker.herokuapp.com/"

function draw_player(player) {

    var card1 = "( "
    player.card1.forEach(card => {
        card1 = card1 + card.name
    });
    card1 = card1 + " )"

    var card2 = "( "
    player.card2.forEach(card => {
        card2 = card2 + card.name
    });
    card2 = card2 + " )"
    
    document.getElementById("hand").innerHTML = card1 + card2
    //document.getElementById("bet").prop('max', player.stack);

}

function draw_table(table) {
    var cards_name = ""
    table.cards.forEach(card => {
        cards_name = cards_name + card.name
    });
    document.getElementById("table_cards").innerHTML = cards_name
    document.getElementById("active").innerHTML = table.current_player
    document.getElementById("pot").innerHTML = table.pot

    var id = new URL(window.location.href).searchParams.get("player")

    document.getElementById("to_call").innerHTML = table.players_to_call[id]

    if (table.finished == 1 && table.showdown == 1){

        var end = "Hand is over. "
        
        table.players.forEach(player => {
            end = end + " Player " + player.number + " had ("
            player.card1.forEach(card => {
                end = end + card.name
            });
            end = end + " ) ("
        
            player.card2.forEach(card => {
                end = end + card.name
            });
            end = end + " )"
        });
        
        document.getElementById("end").innerHTML = end

    }else{
        end = " "
        document.getElementById("end").innerHTML = end
    }

    document.getElementById("p1stack").innerHTML = table.all_players[0].stack
    document.getElementById("p2stack").innerHTML = table.all_players[1].stack

}
async function get_player() {
    var id = new URL(window.location.href).searchParams.get("player")
    var player = await fetch(url + "player/" + id)
    var json = await player.json()
    return json
}

async function get_table() {
    var table = await fetch(url + "table/")
    var json = await table.json()
    return json
}

async function main() {
    var player = await get_player()
    draw_player(player)

    var table = await get_table()
    draw_table(table)
}

async function restart_hand() {
    console.log(await (await fetch(url + "restart_hand/")).text())
    await main()
}

async function check() {
    var id = new URL(window.location.href).searchParams.get("player")
    var answer = await (await fetch(url + "check/" + id)).text()
    document.getElementById('log').value =  document.getElementById('log').value + answer;
    await main()
}

async function call() {
    var id = new URL(window.location.href).searchParams.get("player")
    var answer = await (await fetch(url + "call/" + id)).text()
    document.getElementById('log').value =  document.getElementById('log').value + answer;
    await main()
}

async function raise_bet() {
    var bet = document.getElementById("bet").value
    var id = new URL(window.location.href).searchParams.get("player")
    var answer = await (await fetch(url + "raise_bet/" + id + "/" + bet)).text()
    document.getElementById('log').value =  document.getElementById('log').value + answer;
    await main()
}

async function fold() {
    var id = new URL(window.location.href).searchParams.get("player")
    console.log(await (await fetch(url + "fold/" + id)).text())
    await main()
}

async function quantum_draw1() {
    var id = new URL(window.location.href).searchParams.get("player")
    console.log(await (await fetch(url + "quantum_draw1/" + id)).text())
    await main()
}

async function quantum_draw2() {
    var id = new URL(window.location.href).searchParams.get("player")
    console.log(await (await fetch(url + "quantum_draw2/" + id)).text())
    await main()
}


window.check = check
window.call = call
window.raise_bet = raise_bet
window.fold = fold
window.quantum_draw1 = quantum_draw1
window.quantum_draw2 = quantum_draw2
window.restart_hand = restart_hand

main()
setInterval(main, 1000)

