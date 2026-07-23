"""
Tests unitarios para main.py

Cubre:
- sanitize_filename: limpieza de nombres de archivo
- load_category_url: lectura y búsqueda en categorias.json
- run_scrapy: construcción del comando de Scrapy (mockeando subprocess.run)
- menu: flujo del menú interactivo (mockeando input, run_scrapy y subprocess)

Ejecutar con:
    pytest --verbose test_main.py
    coverage run -m pytest test_main.py && coverage html
"""

import json
import builtins
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import main
from main import sanitize_filename, load_category_url, run_scrapy, menu


# ---------------------------------------------------------------------------
# sanitize_filename
# ---------------------------------------------------------------------------

class TestSanitizeFilename:
    def test_removes_invalid_characters(self):
        result = sanitize_filename('Ropa/Zapatos: "Nike"')
        assert "/" not in result
        assert ":" not in result
        assert '"' not in result

    def test_replaces_each_invalid_char_with_underscore(self):
        result = sanitize_filename("a<b>c:d")
        assert result == "a_b_c_d"

    def test_strips_trailing_dots_and_spaces(self):
        result = sanitize_filename("Electrodomesticos.  ")
        assert result == "Electrodomesticos"

    def test_leaves_normal_text_untouched(self):
        assert sanitize_filename("Mercado") == "Mercado"

    def test_empty_string_returns_empty(self):
        assert sanitize_filename("") == ""

    def test_only_invalid_characters(self):
        result = sanitize_filename('<>:"/\\|?*')
        assert result == "_" * len('<>:"/\\|?*')

    def test_pipe_and_question_mark(self):
        result = sanitize_filename("precio|barato?")
        assert result == "precio_barato_"


# ---------------------------------------------------------------------------
# load_category_url
# ---------------------------------------------------------------------------

class TestLoadCategoryUrl:
    def test_returns_none_when_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(main, "CATEGORIES_FILE", tmp_path / "no_existe.json")
        assert load_category_url("123", "Mercado") is None

    def test_returns_none_when_json_is_invalid(self, tmp_path, monkeypatch):
        fake_file = tmp_path / "categorias.json"
        fake_file.write_text("{no es json valido", encoding="utf-8")
        monkeypatch.setattr(main, "CATEGORIES_FILE", fake_file)

        assert load_category_url("1", "X") is None

    def test_finds_url_by_id_and_builds_absolute_url(self, tmp_path, monkeypatch):
        fake_file = tmp_path / "categorias.json"
        fake_file.write_text(
            json.dumps([{"id": "123", "name": "Mercado", "url": "/mercado"}]),
            encoding="utf-8",
        )
        monkeypatch.setattr(main, "CATEGORIES_FILE", fake_file)

        result = load_category_url("123", "Mercado")
        assert result == "https://www.olimpica.com/mercado"

    def test_builds_absolute_url_when_relative_path_has_no_leading_slash(
        self, tmp_path, monkeypatch
    ):
        fake_file = tmp_path / "categorias.json"
        fake_file.write_text(
            json.dumps([{"id": "1", "name": "X", "url": "categoria-x"}]),
            encoding="utf-8",
        )
        monkeypatch.setattr(main, "CATEGORIES_FILE", fake_file)

        result = load_category_url("1", "X")
        assert result == "https://www.olimpica.com/categoria-x"

    def test_returns_url_unchanged_when_already_absolute(self, tmp_path, monkeypatch):
        fake_file = tmp_path / "categorias.json"
        fake_file.write_text(
            json.dumps(
                [{"id": "1", "name": "X", "url": "https://otrodominio.com/x"}]
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(main, "CATEGORIES_FILE", fake_file)

        result = load_category_url("1", "X")
        assert result == "https://otrodominio.com/x"

    def test_returns_none_when_id_not_found(self, tmp_path, monkeypatch):
        fake_file = tmp_path / "categorias.json"
        fake_file.write_text(
            json.dumps([{"id": "1", "name": "X", "url": "/x"}]),
            encoding="utf-8",
        )
        monkeypatch.setattr(main, "CATEGORIES_FILE", fake_file)

        assert load_category_url("999", "NoExiste") is None

    def test_returns_none_when_url_field_is_empty(self, tmp_path, monkeypatch):
        fake_file = tmp_path / "categorias.json"
        fake_file.write_text(
            json.dumps([{"id": "1", "name": "X", "url": ""}]),
            encoding="utf-8",
        )
        monkeypatch.setattr(main, "CATEGORIES_FILE", fake_file)

        assert load_category_url("1", "X") is None

    def test_matches_id_as_string_even_if_stored_as_int(self, tmp_path, monkeypatch):
        fake_file = tmp_path / "categorias.json"
        fake_file.write_text(
            json.dumps([{"id": 42, "name": "X", "url": "/x"}]),
            encoding="utf-8",
        )
        monkeypatch.setattr(main, "CATEGORIES_FILE", fake_file)

        result = load_category_url("42", "X")
        assert result == "https://www.olimpica.com/x"


# ---------------------------------------------------------------------------
# run_scrapy
# ---------------------------------------------------------------------------

class TestRunScrapy:
    def test_builds_basic_command(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr(main.subprocess, "run", mock_run)

        run_scrapy("OlimpicaCategorySpider")

        args, kwargs = mock_run.call_args
        command = args[0]
        assert command[0] == main.sys.executable
        assert command[1:4] == ["-m", "scrapy", "crawl"]
        assert command[4] == "OlimpicaCategorySpider"
        assert kwargs["cwd"] == str(main.ROOT)
        assert kwargs["check"] is True

    def test_includes_output_flag_with_absolute_path(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr(main.subprocess, "run", mock_run)

        run_scrapy("OlimpicaCategorySpider", output="salida.json")

        command = mock_run.call_args[0][0]
        assert "-o" in command
        output_index = command.index("-o") + 1
        output_path = Path(command[output_index])
        assert output_path.is_absolute()
        assert output_path == main.ROOT / "salida.json"

    def test_keeps_absolute_output_path_unchanged(self, monkeypatch, tmp_path):
        mock_run = MagicMock()
        monkeypatch.setattr(main.subprocess, "run", mock_run)

        absolute_output = tmp_path / "salida.json"
        run_scrapy("OlimpicaCategorySpider", output=str(absolute_output))

        command = mock_run.call_args[0][0]
        output_index = command.index("-o") + 1
        assert command[output_index] == str(absolute_output)

    def test_passes_extra_kwargs_as_scrapy_arguments(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr(main.subprocess, "run", mock_run)

        run_scrapy(
            "OlimpicaProductSpider",
            category_id="123",
            category_name="Mercado",
        )

        command = mock_run.call_args[0][0]
        assert "-a" in command
        assert "category_id=123" in command
        assert "category_name=Mercado" in command

    def test_no_output_flag_when_output_not_given(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr(main.subprocess, "run", mock_run)

        run_scrapy("OlimpicaCategorySpider")

        command = mock_run.call_args[0][0]
        assert "-o" not in command


# ---------------------------------------------------------------------------
# menu (flujo interactivo, con input/run_scrapy mockeados)
# ---------------------------------------------------------------------------

class TestMenu:
    def _mock_inputs(self, monkeypatch, respuestas):
        """Reemplaza input() para que devuelva respuestas en orden."""
        respuestas_iter = iter(respuestas)
        monkeypatch.setattr(builtins, "input", lambda *_args: next(respuestas_iter))

    def test_opcion_invalida_muestra_mensaje(self, monkeypatch, capsys):
        self._mock_inputs(monkeypatch, ["99"])
        menu()
        salida = capsys.readouterr().out
        assert "Opción no válida" in salida

    def test_opcion_1_llama_run_scrapy_con_spider_correcto(self, monkeypatch):
        mock_run_scrapy = MagicMock()
        monkeypatch.setattr(main, "run_scrapy", mock_run_scrapy)
        self._mock_inputs(monkeypatch, ["1"])

        menu()

        mock_run_scrapy.assert_called_once_with(
            "OlimpicaCategorySpider", output="Olimpica_categorias.json"
        )

    def test_opcion_4_llama_spider_de_falabella(self, monkeypatch):
        mock_run_scrapy = MagicMock()
        monkeypatch.setattr(main, "run_scrapy", mock_run_scrapy)
        self._mock_inputs(monkeypatch, ["4"])

        menu()

        mock_run_scrapy.assert_called_once_with(
            "FalabellaCategorySpider", output="falabella_categorias.json"
        )

    def test_opcion_6_llama_spider_de_linio(self, monkeypatch):
        mock_run_scrapy = MagicMock()
        monkeypatch.setattr(main, "run_scrapy", mock_run_scrapy)
        self._mock_inputs(monkeypatch, ["6"])

        menu()

        mock_run_scrapy.assert_called_once_with(
            "LinioCategorySpider", output="linio_categorias.json"
        )

    def test_opcion_3_sin_archivo_categorias_muestra_aviso(
        self, monkeypatch, tmp_path, capsys
    ):
        monkeypatch.setattr(main, "CATEGORIES_FILE", tmp_path / "no_existe.json")
        self._mock_inputs(monkeypatch, ["3"])

        menu()

        salida = capsys.readouterr().out
        assert "extrae las categorías primero" in salida

    def test_opcion_3_lista_categorias_existentes(self, monkeypatch, tmp_path, capsys):
        fake_file = tmp_path / "categorias.json"
        fake_file.write_text(
            json.dumps([{"id": "1", "name": "Mercado"}]), encoding="utf-8"
        )
        monkeypatch.setattr(main, "CATEGORIES_FILE", fake_file)
        self._mock_inputs(monkeypatch, ["3"])

        menu()

        salida = capsys.readouterr().out
        assert "Mercado" in salida
        assert "ID: 1" in salida

    def test_opcion_7_construye_nombre_de_salida_sanitizado(self, monkeypatch):
        mock_run_scrapy = MagicMock()
        monkeypatch.setattr(main, "run_scrapy", mock_run_scrapy)
        # Respuestas en orden: category_id, category_name, max_pages
        self._mock_inputs(monkeypatch, ["7", "CATG123", 'Ropa/Deportiva"', ""])

        menu()

        _, kwargs = mock_run_scrapy.call_args
        assert kwargs["category_id"] == "CATG123"
        assert "/" not in kwargs["output"]
        assert '"' not in kwargs["output"]
        assert kwargs["max_pages"] == "3"  # valor por defecto

    def test_opcion_2_lanza_error_sin_nombre_ni_url(self, monkeypatch, tmp_path):
        monkeypatch.setattr(main, "CATEGORIES_FILE", tmp_path / "no_existe.json")
        mock_run_scrapy = MagicMock()
        monkeypatch.setattr(main, "run_scrapy", mock_run_scrapy)
        # category_id, category_name vacío, max_sections vacío
        self._mock_inputs(monkeypatch, ["2", "1", "", ""])

        with pytest.raises(ValueError):
            menu()