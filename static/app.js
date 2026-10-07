document.addEventListener("DOMContentLoaded", () => {
  const botoesCliente = document.querySelectorAll(".client-select");
  const placeholder = document.querySelector("[data-selected-placeholder]");
  const conteudoSelecionado = document.querySelector("[data-selected-content]");
  const acoesSelecionadas = document.querySelector("[data-selected-actions]");
  const editarSelecionado = document.querySelector("[data-edit-selected]");
  const excluirSelecionado = document.querySelector("[data-delete-selected]");

  botoesCliente.forEach((botao) => {
    botao.addEventListener("click", () => {
      botoesCliente.forEach((outroBotao) => {
        const selecionado = outroBotao === botao;
        outroBotao.setAttribute("aria-pressed", String(selecionado));
        outroBotao.closest(".client-row").classList.toggle("selected", selecionado);
      });

      placeholder.hidden = true;
      conteudoSelecionado.hidden = false;
      acoesSelecionadas.hidden = false;
      conteudoSelecionado.querySelector("[data-selected-name]").textContent =
        botao.dataset.clientName;
      const contato = [botao.dataset.phone, botao.dataset.email]
        .filter(Boolean)
        .join(" • ");
      conteudoSelecionado.querySelector("[data-selected-contact]").textContent =
        contato;
      conteudoSelecionado.querySelector(
        "[data-selected-observations]",
      ).textContent = botao.dataset.observations
        ? `Observações: ${botao.dataset.observations}`
        : "Sem observações.";
      editarSelecionado.href = botao.dataset.editUrl;
      excluirSelecionado.action = botao.dataset.deleteUrl;
      excluirSelecionado.dataset.clientName = botao.dataset.clientName;
    });
  });

  document.querySelectorAll(".confirm-delete").forEach((formulario) => {
    formulario.addEventListener("submit", (evento) => {
      const nome = formulario.dataset.clientName;
      if (!window.confirm(`Deseja excluir ${nome}?`)) {
        evento.preventDefault();
      }
    });
  });
});
