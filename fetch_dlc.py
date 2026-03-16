from bs4 import BeautifulSoup
import requests
import time

class FetchDLCWiki:
    """Extrae DLC de mapa (Map Expansion / States) desde trucksimulator.wiki.gg."""

    URL_ETS2 = "https://trucksimulator.wiki.gg/wiki/Downloadable_Content/Euro_Truck_Simulator_2"
    URL_ATS = "https://trucksimulator.wiki.gg/wiki/Downloadable_Content/American_Truck_Simulator"

    def __init__(self):
        self.dlc_ets2 = []
        self.dlc_ats = []

    def _request(self, url):
        r = requests.get(url, timeout=30)
        r.encoding = "utf-8"
        return BeautifulSoup(r.text, "html.parser")

    def _dlcs_from_table(self, soup, header_contains):
        """Extrae nombres de DLC de la tabla cuya cabecera contiene header_contains."""
        result = []
        content = (
            soup.select_one("div.mw-content-text")
            or soup.select_one("div.bodyContent")
            or soup.select_one("div.mw-parser-output")
        )
        if not content:
            content = soup
        for table in content.find_all("table"):
            if "navbox" in (table.get("class") or []):
                continue
            header_cells = table.find_all("th")
            header_text = " ".join(th.get_text(strip=True) for th in header_cells).lower()
            if header_contains not in header_text:
                continue
            for tr in table.find_all("tr"):
                first_td = tr.find("td")
                if not first_td:
                    continue
                link = first_td.find("a", href=True)
                if not link:
                    continue
                name = (link.get("title") or link.get_text(strip=True)).strip()
                if not name or name in result:
                    continue
                # ETS2: quitar prefijo "Euro Truck Simulator 2: "
                if name.startswith("Euro Truck Simulator 2: "):
                    name = name[len("Euro Truck Simulator 2: ") :].strip()
                result.append(name)
        return result

    def get_dlc_ets2(self):
        """Solo Map Expansion (tabla con columna Cities)."""
        soup = self._request(self.URL_ETS2)
        self.dlc_ets2 = self._dlcs_from_table(soup, "cities")
        return self.dlc_ets2

    def get_dlc_ats(self):
        """Solo States (tabla con columna Capital)."""
        soup = self._request(self.URL_ATS)
        self.dlc_ats = self._dlcs_from_table(soup, "capital")
        return self.dlc_ats

    def get_all_dlc_json(self):
        """Lista para JSON: [{"name": "...", "game": "ets2"|"ats"}, ...]."""
        self.get_dlc_ets2()
        self.get_dlc_ats()
        dlcs = [{"name": n, "game": "ets2"} for n in self.dlc_ets2]
        dlcs += [{"name": n, "game": "ats"} for n in self.dlc_ats]
        return {
            "updated_at": int(time.time()),
            "dlcs": dlcs,
        }
