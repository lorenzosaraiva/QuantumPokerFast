	function draw_player(player){
		
		document.getElementById("p1stack").innerHTML = player.stack
	}

	function draw_table(table){
        console.log(table)
        var cards_name = ""
        table.cards.forEach(card => {
            cards_name = cards_name + card.name
        });
		document.getElementById("table_cards").innerHTML = cards_name
	}
	async function get_player(){
		var player = await fetch("http://127.0.0.1:8000/player/0")
		var json = await player.json()
		return json
	}

	async function get_table(){
		var table = await fetch("http://127.0.0.1:8000/table")
		var json = await table.json()
		return json
	}

	async function main(){
		var player = await get_player()
		draw_player(player)
		
		var table = await get_table()
		draw_table(table)
	}

	async function check(){
		await fetch("http://127.0.0.1:8000/check")
		await main()
	}

	window.check = check
	
	main()

