// Preenche os "id" que estão null em caixa_1.json usando a API da YGOPRODeck.
// Uso: node preencher_ids.js   (Node 18+)
const fs = require("fs");
 
(async () => {
  const cartas = JSON.parse(fs.readFileSync("caixa_1.json", "utf-8"));
  const url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?cardset=" +
              encodeURIComponent("Legend of Blue Eyes White Dragon");
  const { data } = await (await fetch(url)).json();
  const porNome = new Map(data.map(c => [c.name.toLowerCase(), String(c.id)]));
 
  const naoEncontradas = [];
  for (const c of cartas) {
    const id = porNome.get(c.nome.toLowerCase());
    if (!id) naoEncontradas.push(c.nome);
    else c.id = id; // sobrescreve também os que já tinham id, para garantir consistência
  }
 
  fs.writeFileSync("caixa_1.json", JSON.stringify(cartas, null, 2), "utf-8");
  console.log(`OK: ${cartas.length - naoEncontradas.length}/${cartas.length} ids preenchidos.`);
  if (naoEncontradas.length) console.log("Sem match na API:", naoEncontradas);
})();