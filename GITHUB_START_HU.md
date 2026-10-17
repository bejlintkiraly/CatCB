# CatCB GitHubra feltöltés – magyar útmutató

## Mi került kitisztításra?
- Kikerültek a forrásból a beégetett céges To/CC e-mail-címek.
- Az e-mail-készítő üres címzettmezőkkel indul, általános IT-operations tárgyat és mintaszöveget használ.
- Nem került bele `state.json`, személyes snippet-könyvtár, EXE, buildnapló vagy e-mail-fájl.
- A helyi fájlok és buildkimenetek kizárása bekerült a `.gitignore`-ba.
- A `Bejlint` márkajelzés megmaradt, mert ez szándékos alkalmazásbranding.

## Ajánlott GitHub-beállítás
Első körben **Private** repositoryt hozz létre. Ne adj hozzá automatikusan LICENSE fájlt: előbb döntsd el, szeretnéd-e, hogy mások jogilag újrahasználhassák a kódot.

1. GitHubon válaszd a **New repository** lehetőséget.
2. Repository name: `CatCB`.
3. Description: `A personal IT snippet manager with Outlook template tools.`
4. Visibility: **Private**.
5. Ne generálj külön README-t, `.gitignore`-t vagy licencet, mert ezek ebben a csomagban már benne vannak.
6. Hozd létre a repositoryt, majd válaszd az **Add file → Upload files** opciót.
7. A kicsomagolt `CatCB_GitHub_Starter_v1.10.2` mappa tartalmát töltsd fel (a mappa nevét önmagában ne egyetlen fájlként töltsd fel).
8. Commit message: `Add sanitized CatCB v1.10.2 baseline`.
9. Ellenőrizd a repository fájllistáját és a `index.html` forrásban, hogy nincs benne céges címzett.

A GitHub webes felülete legfeljebb 100 fájlt enged egyszerre feltölteni, és fájlonként 25 MiB a webes limit; ez a forráscsomag kényelmesen a határon belül van. A fájlok feltöltése előtt vizsgáld át a változásokat.

## Fontos
Ez a repository starter csomag, nem hoz létre automatikusan repo-t a GitHub-fiókodban. A ChatGPT innen nincs közvetlenül hitelesítve a GitHub-fiókodba, ezért az első feltöltést te végzed a webes felületen. Ha később GitHub Desktopot használsz, könnyebb lesz a verziókezelés és az új build feltöltése.
