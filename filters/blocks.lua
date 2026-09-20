--[[
  blocks.lua - bloques de contenido del libro.

  Se ejecuta DESPUÉS de los filtros de Quarto (véase `filters:` en _quarto.yml),
  de modo que las cabeceras de los entornos numerados (Supuesto, Definición,
  Ejemplo, Ejercicio) ya existen cuando las reformatea.

  Hace tres cosas:
   1. Convierte los divs sin numeración (.intuicion, .cuidado, .solucion,
      .pregunta, .datos-usados) en entornos LaTeX propios; en HTML los deja
      intactos porque styles/book.scss se encarga de ellos.
   2. Envuelve las soluciones en <details> en HTML y las omite por completo
      cuando `mostrar-soluciones: false`.
   3. Sustituye los paréntesis del nombre en las cabeceras de los entornos
      numerados por un punto medio: "Supuesto 5.1 (nombre)" -> "Supuesto 5.1 · nombre".

  Convención: dentro de un .panel-tabset los títulos de pestaña se escriben
  como encabezados de nivel 4 (####). Con number-depth: 2 y toc-depth: 2 salen
  en el PDF como etiqueta sin numerar y no entran en el índice.
--]]

local show_solutions = true

local latex_env = {
  intuicion = "intuicionblock",
  cuidado = "cuidadoblock",
  solucion = "solucionblock",
  pregunta = "preguntablock",
  ["datos-usados"] = "datosblock",
}

local html_label = {
  intuicion = "Intuición",
  cuidado = "Cuidado",
  pregunta = "La pregunta económica",
  ["datos-usados"] = "Datos utilizados",
}

local function has_class(el, name)
  for _, c in ipairs(el.classes) do
    if c == name then return true end
  end
  return false
end

function Meta(meta)
  local v = meta["mostrar-soluciones"]
  if v ~= nil then
    if type(v) == "boolean" then
      show_solutions = v
    else
      show_solutions = (pandoc.utils.stringify(v) ~= "false")
    end
  end
  return meta
end

function Div(el)
  for class, env in pairs(latex_env) do
    if has_class(el, class) then
      if class == "solucion" and not show_solutions then
        return {}
      end
      if quarto.doc.is_format("latex") then
        local out = pandoc.List({ pandoc.RawBlock("latex", "\\begin{" .. env .. "}") })
        out:extend(el.content)
        out:insert(pandoc.RawBlock("latex", "\\end{" .. env .. "}"))
        return out
      elseif quarto.doc.is_format("html") and class == "solucion" then
        local out = pandoc.List({ pandoc.RawBlock("html",
          '<details class="solucion"><summary>Ver solución</summary><div class="solucion-cuerpo">') })
        out:extend(el.content)
        out:insert(pandoc.RawBlock("html", "</div></details>"))
        return out
      end
      return el
    end
  end
  return el
end

-- "Supuesto 5.1 (Identificación recursiva)" -> "Supuesto 5.1 · Identificación recursiva"
function Span(el)
  if not quarto.doc.is_format("html") then return el end
  if not has_class(el, "theorem-title") then return el end
  local inlines = el.content
  if #inlines == 1 and inlines[1].t == "Strong" then
    local inner = inlines[1].content
    local text = pandoc.utils.stringify(inner)
    local head, note = text:match("^(.-)%s*%((.+)%)%s*$")
    if head and note then
      inlines[1].content = pandoc.Inlines({
        pandoc.Str(head), pandoc.Space(), pandoc.Str("·"), pandoc.Space(), pandoc.Str(note) })
      el.content = inlines
    end
  end
  return el
end

return { { Meta = Meta }, { Div = Div, Span = Span } }
