#!/usr/bin/env python3
###############################################################################
## vim: et ai ts=4
##
import os
import re
import argparse as ap
from typing import TypeVar, TypedDict

T = TypeVar("T", int, float, complex, str, bool)


class Student(TypedDict):
    matnr: int
    nachname: str
    vorname: str


class IndentProfile(TypedDict):
    indent: list[str]
    profile: list[int]


class Block(TypedDict):
    startline: int
    endline: int


class Namespace(ap.Namespace):
    delimiter: str
    quiet: int
    implfiles: list[str]


class ParsedCode(TypedDict):
    codelines: list[str]
    indentprofile: IndentProfile
    patternClass: list[int]
    patternDef: list[int]
    patternImport: list[int]
    patternFromImport: list[int]
    patternBlankLine: list[int]
    patternLineComment: list[int]
    patternAufgabe: list[int]
    patternStudentenLD: list[int]
    patternStudentenAP: list[int]
    patternGruppe: list[int]
    ClassBlocks: list[Block]
    DefBlocks: list[Block]
    ClassDefCover: list[int]


class Grading:
    ###########################################################################
    ## Statische Variablen und Funktionen
    ##
    ClassPattern = r"^\s*class\s+(?=[a-zA-Z_])"
    DefPattern = r"^\s*def\s+(?=[a-zA-Z_])"
    IndentPattern = r"^[ \t]*"
    ImportPattern = r"^\s*import\s+(?=[a-zA-Z_])"
    FromImportPattern = r"^\s*from\s.*\simport\s"
    BlankLinePattern = r"^\s*$"
    LineCommentPattern = r"^\s*#"
    AufgabePattern = r"^Aufgabe\s*=\s*\d+"
    StudentenLDPattern = r"^Studenten\s*=\s*\[\]"
    StudentenAPPattern = r"^Studenten.append\(\{"
    GruppenPattern = r"^Gruppennummer\s*=\s*\d+"

    ###############################################################################
    ## Checkfunktion: Diese Funktion prueft, ob die Gruppennummer und die Eintaege
    ##                der Studentendaten im richtigen Format vorliegen.
    @staticmethod
    def CheckStudents(
        students: list[Student],
        group: int,
        task: int,
        maxStudents: int = 7,
        ExOK: bool = False,
        printList: bool = True,
    ) -> bool:
        ## Pruefe den Variablentyp:
        assert isinstance(group, int), "Die Gruppennummer muss eine Zahl sein!"
        assert ExOK or group != 0, (
            "Die Gruppennummer ist noch mit dem Beispieleintrag versehen!"
        )
        assert group >= 0, "Die Gruppennummer muss eine positve Zahl sein!"
        assert isinstance(students, list), (
            "Die Studenten muessen in einer Liste stehen!"
        )
        assert isinstance(task, int), "Die Aufgabennummer muss eine Zahl sein!"
        assert ExOK or task != 0, (
            "Die Aufgabennummer ist noch mit dem Beispieleintrag versehen!"
        )
        assert task >= 0, "Die Aufgabennummer muss eine positve Zahl sein!"

        ## Da die Variable students eine Liste ist, hat sie auch eine Laenge:
        studentCount = len(students)
        assert 0 < studentCount <= maxStudents, (
            "Die Anzahl der Studenten muss zwischen 1 und %i liegen!" % (maxStudents)
        )

        ## Um dauf Mehrfacheintraege hin zu pruefen, werden folgende Listen
        ## initalisiert:
        MatNr = []
        Namen = []

        ## Es werden nun nacheinander alle Listeneintraege von students geprueft:
        for person in range(studentCount):
            ## Pruefe den Variablentyp des xten Eintrags der Liste:
            assert isinstance(students[person], dict), (
                "Der Eintrag fuer den %i. Studenten muss ein Dictionary Eintrag sein!"
                % (person + 1)
            )

            ## Pruefe den Schluessel 'matnr' auf notwendige Eigenschaften:
            assert "matnr" in students[person], (
                "Der Eintrag fuer den %i. Studenten muss den Schluessel 'matnr' haben!"
                % (person + 1)
            )
            assert isinstance(students[person]["matnr"], int), (
                "Die Matrikelnummer des %i. Studenten muss eine Zahl sein!"
                % (person + 1)
            )
            assert (9999 < students[person]["matnr"] <= 99999) or (
                999999 < students[person]["matnr"] <= 9999999
            ), (
                "Die Matrikelnummer des %i. Studenten muss fuenf- oder siebenstellig sein!"
                % (person + 1)
            )
            assert ExOK or students[person]["matnr"] / 10 != 1234, (
                "Die Matrikelnummer des %i. Studenten ist noch mit dem Beispieleintrag versehen!"
                % (person + 1)
            )

            ## Pruefe den Schluessel 'nachname' auf notwendige Eigenschaften:
            assert "nachname" in students[person], (
                "Der Eintrag fuer den %i. Studenten muss den Schluessel 'nachname' haben!"
                % (person + 1)
            )
            assert isinstance(students[person]["nachname"], str), (
                "Der Nachname des %i. Studenten muss ein String sein!" % (person + 1)
            )
            assert len(students[person]["nachname"]) > 1, (
                "Der Nachname des %i. Studenten muss mindestens 2 Zeichen lang sein!"
                % (person + 1)
            )
            assert ExOK or students[person]["nachname"][:8] != "NACHNAME", (
                "Der Nachname des %i. Studenten ist noch mit dem Beispieleintrag versehen!"
                % (person + 1)
            )

            ## Pruefe den Schluessel 'vorname' auf notwendige Eigenschaften:
            assert "vorname" in students[person], (
                "Der Eintrag fuer den %i. Studenten muss den Schluessel 'vorname' haben!"
                % (person + 1)
            )
            assert isinstance(students[person]["vorname"], str), (
                "Der Vorname des %i. Studenten muss ein String sein!" % (person + 1)
            )
            assert len(students[person]["vorname"]) > 1, (
                "Der Vorname des %i. Studenten muss mindestens 2 Zeichen lang sein!"
                % (person + 1)
            )
            assert ExOK or students[person]["vorname"][:7] != "VORNAME", (
                "Der Vorname des %i. Studenten ist noch mit dem Beispieleintrag versehen!"
                % (person + 1)
            )

            ## Vorbereitung auf Dubletten Check beim Namen und der Matrikelnummer
            MatNr.append(students[person]["matnr"])
            Namen.append(students[person]["vorname"] + students[person]["nachname"])

        ## Dubletten Check beim Namen und der Matrikelnummer
        assert studentCount == len(set(MatNr)), (
            "Bei den Matrikelnummern kommt mindestens eine Nummer mehrfach vor!"
        )
        assert studentCount == len(set(Namen)), (
            "Bei den Namen kommt mindestens ein Name mehrfach vor!"
        )

        ## Die Eintraege befinden sich in der Korrekten Form fuer die automatische
        ## Ueberpruefung
        if printList:
            print("\n====================")
            print("Aufgabe:       %02i" % (task))
            print("Gruppennummer: %02i\n" % (group))
            print("Matrikelnummer, Name")
            print("--------------------")
            for person in range(studentCount):
                d = students[person]
                print("%14i, %s %s" % (d["matnr"], d["vorname"], d["nachname"]))
            print("====================\n")
        return True

    ###########################################################################
    ## Einlesen der Python Uebungsaufgabe
    ##
    @staticmethod
    def ReadExercise(filename: str, chkPython: bool = True) -> list[str]:
        # Existenzcheck
        assert os.path.exists(filename)
        assert os.path.isfile(filename)
        # Einlesen der Datei
        codelines = open(filename, "r").readlines()
        # Pruefen, ob die Datei nicht leer ist
        assert len(codelines) > 0
        # Optionale Pruefung, ob die Datei eine Python Datei ist.
        assert chkPython or codelines[0].find("#!/usr/bin/env python3") > -1
        return codelines

    ###########################################################################
    ## Entfernt Zeilenkommentare
    ##
    @staticmethod
    def StripLineComments(codelines: list[str]) -> list[str]:
        assert isinstance(codelines, list)
        ret = []
        for line in codelines:
            # beginnt die Zeile nicht mit beliebig vielen Leerzeichen gefolgt
            # von "#", so wird diese an den Rueckgabewert angehaengt
            # Das entfernen von Kommentaren in der selben Zeile wie eine
            # Programmanweisung ist nicht so einfach, da man vorher
            # Pruefen muss, ob das "#"-Zeichen nicht innerhalb eines Strings
            # steht.
            if line.lstrip().find("#") != 0:
                ret.append(line)
        return ret

    ###########################################################################
    ## Entfernt Leere Zeilen (Whitespaces koennen vorkommen)
    ##
    @staticmethod
    def StripBlankLines(codelines: list[str]) -> list[str]:
        assert isinstance(codelines, list)
        ret = []
        for line in codelines:
            # lstrip entfernt Whitespaces von Links inkl. "\n"
            if len(line.lstrip()) != 0:
                ret.append(line)
        return ret

    ###########################################################################
    ## Entfernt aus der eingelesenen Pyton Datei alles nach
    ## if __name__ == "__main__":
    ## Vorher sollte StripLineComments angewendet werden!
    ##
    @staticmethod
    def StripIfMain(codelines: list[str]) -> list[str]:
        assert isinstance(codelines, list)
        ret = []
        r1 = re.compile(r"^\s*if\s+__name__\s*==\s*[\"']__main__[\"']\s*:")
        for line in codelines:
            # For-Schleife wird abgebrochen, wenn
            if len(r1.findall(line)) != 0:
                break
            ret.append(line)
        return ret

    ###########################################################################
    ## Gibt die Zeilennummern der Zeilen zurueck, auf die der Matchstring
    ## passt (funktioniert aehnlich wie find fkt bei Strings).
    ## Mit start und stop kann dabei das zu untersuchende Interval im Code
    ## eingeschraenkt werdn.
    ##
    @staticmethod
    def FindLines(
        pattern: str,
        codelines: list[str],
        start: int | None = None,
        stop: int | None = None,
        correctNumbering: bool = True,
    ) -> list[int]:
        assert isinstance(pattern, str) and len(pattern) > 0
        assert isinstance(codelines, list) and len(codelines) > 0
        assert isinstance(start, int) or start is None
        assert isinstance(stop, int) or stop is None
        assert len(codelines[start:stop]) > 0
        ret = []
        r1 = re.compile(pattern)
        correction = 0
        if correctNumbering:
            # Korrigiert die Zeilennummern bei start != None:
            correction = range(len(codelines))[start:stop][0]

        checklines = codelines[start:stop]
        for lnr in range(len(checklines)):
            if len(r1.findall(checklines[lnr])) > 0:
                ret.append(lnr + correction)
        return ret

    ###########################################################################
    ## Gibt ein Einrueckungsprofil zurueck.
    ##
    @staticmethod
    def GetIndentProfile(
        codelines: list[str],
        start: int | None = None,
        stop: int | None = None,
        tabsize: int = 4,
    ) -> IndentProfile:
        assert isinstance(codelines, list) and len(codelines) > 0
        assert isinstance(start, int) or start is None
        assert isinstance(stop, int) or stop is None
        assert isinstance(tabsize, int)
        assert len(codelines[start:stop]) > 0
        ret: IndentProfile = {"indent": [], "profile": []}
        r1 = re.compile(Grading.IndentPattern)
        for line in codelines[start:stop]:
            ind = r1.findall(line)[0]
            ret["indent"].append(ind)
            ret["profile"].append(len(ind.replace("\t", " " * tabsize)))
        return ret

    ###########################################################################
    ## Vergleicht das Ergebnis der Testroutine mit einem Korrekturschluessel.
    ## Die Listen duerfen str, Zahlen oder Bool  enthalten. Ist ein Fehler
    ## aufgetreten, so wird in result None Eingetragen.
    ## Stimmen die Laengen der Ergebnislisten nicht ueberein, dann wird
    ## result durch [None for p in masterresult] ersetzt.
    ## allowLessResults==True -> Fehlende Ergebnisse werden am Ende der
    ##                           result Liste durch None ergaenzt
    ## allowMoreResults==True -> Laenge von result wird auf die laenge von
    ##                           masterresult gekuerzt
    ##
    @staticmethod
    def CheckResult(
        result: list[T | None],
        masterresult: list[T],
        txtresult: list[str],
        allowLessResults: bool = False,
        allowMoreResults: bool = False,
        delim: str = "@",
        filename: str = "output",
        printresult: bool = True,
    ) -> None:
        assert isinstance(result, list)
        assert isinstance(masterresult, list) and len(masterresult) > 0
        assert isinstance(txtresult, list) and len(txtresult) == len(result)
        assert isinstance(allowLessResults, bool)
        assert isinstance(allowMoreResults, bool)
        assert isinstance(delim, str) and len(delim) > 0
        assert isinstance(filename, str) and len(filename) > 0
        assert isinstance(printresult, bool)
        # Pruefe jeden Eintrag von result und masterresult auf den richtigen Datentyp
        for x in result:
            assert isinstance(x, (int, float, complex, str, bool)) or x is None
        for x in masterresult:
            assert isinstance(x, (int, float, complex, str, bool))

        # Resultat ggf. anpassen:
        lr = len(result)
        lt = len(txtresult)
        lm = len(masterresult)
        if lr < lm:
            if allowLessResults:
                result.extend([None for p in range(lm - lr)])
                txtresult.extend(["" for p in range(lm - lt)])
            else:
                result = [None for p in masterresult]
                txtresult.extend(["" for p in range(lm - lt)])
        if lr > lm:
            if allowMoreResults:
                result = result[: (lm - 1)]
            else:
                result = [None for p in masterresult]
        fout = []

        # Vergleichen der Ergebnisse
        for i in range(lm):
            if result[i] is None or type(result[i]) is not type(masterresult[i]):
                fout.append(-1)
                erg = "Unerwarteter Fehler!"
            elif result[i] == masterresult[i]:
                fout.append(1)
                erg = "      Bestanden "
            else:
                fout.append(0)
                erg = "Nicht Bestanden!"
            if printresult:
                print("%3i. Test: %s (%s)" % (i + 1, erg, txtresult[i]))

        try:
            f = open(filename, "w")
            f.write(delim.join(list(map(str, fout))) + delim)
            f.close()
        except IOError as e:
            print("Fehler beim Schreiben der '%s' Datei.\n" % (filename), e)

    ###########################################################################
    ## Parser fuer Programmargumente
    ##
    @staticmethod
    def ParseCMD() -> Namespace:
        parser = ap.ArgumentParser(description="Testscript for Autograder.")
        parser.add_argument(
            "-d",
            "--delimiter",
            dest="delimiter",
            default="@",
            help="Delimiter used to separate tests in the output file.",
        )
        parser.add_argument(
            "-q",
            "--quiet",
            dest="quiet",
            default=0,
            action="count",
            help="Produce no output except for errors (used in batchmode).",
        )
        parser.add_argument(
            "implfiles",
            nargs="+",
            help="Name of students' implemntation file(s), e. g. 'uebung.py'.",
        )
        ns = Namespace()
        parser.parse_args(namespace=ns)
        # args hat folgende Eintraege:
        # args.delimiter        <- Character
        # args.quiet            <- Bool
        # args.implfiles        <- Liste
        return ns

    ###########################################################################
    ## Gibt den Quellcode von Zeile start bis stop (ohne stop) aus und markiert die
    ## Zeilennummern aus der Liste mit der Marke
    ##
    @staticmethod
    def PrintLines(
        codelines: list[str],
        marklist: list[int],
        marker: str = "-->",
        start: int | None = None,
        stop: int | None = None,
    ) -> None:
        assert isinstance(codelines, list) and len(codelines) > 0
        assert isinstance(marklist, list)
        assert isinstance(marker, str) and 0 < len(marker) < 4
        assert isinstance(start, int) or start is None
        assert isinstance(stop, int) or stop is None
        assert len(codelines[start:stop]) > 0

        NeedMarker = len(marklist) > 0
        lnr = range(len(codelines))[start:stop][0] + 1
        for line in codelines[start:stop]:
            if NeedMarker:
                if (lnr - 1) in marklist:
                    m = marker
                else:
                    m = ""
                print("%3s [%3d]: %s" % (m, lnr, line), end="")
            else:
                print("[%3d]: %s" % (lnr, line), end="")
            lnr += 1

    ###########################################################################
    ## Bestimmt das Ende des Codeblocks, der in Zeile startline beginnt.
    ## Typischer weise wird eine Funktions- oder Klassendefinition als line
    ## gewaehlt. Zurueckgegeben wird die Zeile, bevor der naechste Block
    ## beginnt. In Skiplines wird eine Liste von Zeilen angegeben, die
    ## nicht betrachtet werden sollen (z.B. Leerzeilen und Zeilenkommentare).
    ## Die Funktion stuetzt sich auf das Ergebnis von GetIndetProfile
    @staticmethod
    def FindBlock(startline: int, profile: list[int], skiplines: list[int]) -> int:
        assert isinstance(startline, int) and startline >= 0
        assert isinstance(profile, list) and len(profile) > startline
        assert isinstance(skiplines, list)
        assert startline not in skiplines

        endline = startline
        startIndent = profile[startline]
        for lnr in range(startline + 1, len(profile)):
            if lnr in skiplines:
                continue

            if profile[lnr] > startIndent:
                endline = lnr
            else:
                break
        return endline

    ###############################################################################
    ## Parsen des Codes
    ##
    @staticmethod
    def ParseCode(filename: str) -> ParsedCode:
        assert isinstance(filename, str)
        codelines = Grading.StripIfMain(Grading.ReadExercise(filename))
        # ret: ParsedCode = {
        ret: ParsedCode = {
            # Einlesen der Datei und entfernen des 'if __name__ ==...' Blocks
            "codelines": codelines,
            # Einrueckungsprofil bestimmen
            "indentprofile": Grading.GetIndentProfile(codelines),
            # Interessante Codemuster suchen
            "patternClass": Grading.FindLines(Grading.ClassPattern, codelines),
            "patternDef": Grading.FindLines(Grading.DefPattern, codelines),
            "patternImport": Grading.FindLines(Grading.ImportPattern, codelines),
            "patternFromImport": Grading.FindLines(
                Grading.FromImportPattern, codelines
            ),
            "patternBlankLine": Grading.FindLines(Grading.BlankLinePattern, codelines),
            "patternLineComment": Grading.FindLines(
                Grading.LineCommentPattern, codelines
            ),
            "patternAufgabe": Grading.FindLines(Grading.AufgabePattern, codelines),
            "patternStudentenLD": Grading.FindLines(
                Grading.StudentenLDPattern, codelines
            ),
            "patternStudentenAP": Grading.FindLines(
                Grading.StudentenAPPattern, codelines
            ),
            "patternGruppe": Grading.FindLines(Grading.GruppenPattern, codelines),
            "ClassBlocks": [],
            "DefBlocks": [],
            "ClassDefCover": [],
        }

        # Bestimme die Codebloecke
        for startline in ret["patternClass"]:
            endline = Grading.FindBlock(
                startline,
                ret["indentprofile"]["profile"],
                ret["patternBlankLine"] + ret["patternLineComment"],
            )
            ret["ClassBlocks"].append({"startline": startline, "endline": endline})
        for startline in ret["patternDef"]:
            endline = Grading.FindBlock(
                startline,
                ret["indentprofile"]["profile"],
                ret["patternBlankLine"] + ret["patternLineComment"],
            )
            ret["DefBlocks"].append({"startline": startline, "endline": endline})

        # Bestimme die Zeilen, die innerhalb der Klassen und Definitionen liegen
        # Alle Zeilen auserhalb stellen Zeilen mit potentziellem Schadcode dar
        s: set[int] = set()
        for rng in ret["ClassBlocks"] + ret["DefBlocks"]:
            s = s.union(range(rng["startline"], rng["endline"] + 1))
        ret["ClassDefCover"] = list(s)
        return ret

    ###############################################################################
    ## Vortest: - Prueft Studenten, Gruppennummer, Aufgabe
    ##          - Prueft ob zu testende Strukturen definiert sind
    ##          - Prueft erlaubten Strukturen ausserhalb von Klassen und Funktionen
    @staticmethod
    def PreTest(
        parsedCode: ParsedCode,
        toTestPatterns: list[str],
        allowedStructuresPatterns: list[str],
        quiet: bool,
    ) -> bool:
        assert isinstance(parsedCode, dict)
        assert isinstance(toTestPatterns, list) and len(toTestPatterns) > 0
        assert isinstance(allowedStructuresPatterns, list)

        # Pruefe zu testende Strukturen
        for ptrn in toTestPatterns:
            if len(Grading.FindLines(ptrn, parsedCode["codelines"])) == 0:
                if not quiet:
                    raise AssertionError(
                        "Das Muster '%s' fuer eine zu testende Struktur wurde nicht gefunden.\n"
                        % (ptrn)
                    )
                return False

        # Pruefe auf erlaubte Strukturen
        s = set(range(len(parsedCode["codelines"])))  # Alle Zeilennummern des Codes
        # Grundsatzlich sind Klassen- und Funktionsdefinitionen, Studenten, Gruppennummer
        #   Aufgabe, Leerzeilen, Zeilenkommentare erlaubt.
        s -= set(parsedCode["ClassDefCover"])
        s -= set(parsedCode["patternStudentenLD"])
        s -= set(parsedCode["patternStudentenAP"])
        s -= set(parsedCode["patternGruppe"])
        s -= set(parsedCode["patternAufgabe"])
        s -= set(parsedCode["patternBlankLine"])
        s -= set(parsedCode["patternLineComment"])
        # Nun noch die explizit erlaubten Strukturen
        for ptrn in allowedStructuresPatterns:
            s -= set(Grading.FindLines(ptrn, parsedCode["codelines"]))
        # s sollte jetzt leer sein.
        if len(s) > 0:
            if not quiet:
                Grading.PrintLines(parsedCode["codelines"], list(s))
                raise AssertionError("Der Code Enthaelt nicht erlaubte Strukturen!")
            return False

        # Pruefe die Eintraege fuer Studenten, Gruppen und Aufgabennummer
        if len(parsedCode["patternGruppe"]) == 0:
            if not quiet:
                raise AssertionError("Gruppennummer ist nicht definiert!")
            return False
        toExecute = list(
            map(lambda x: parsedCode["codelines"][x], parsedCode["patternGruppe"])
        )
        if len(parsedCode["patternAufgabe"]) == 0:
            if not quiet:
                raise AssertionError("Aufgabennummer ist nicht definiert!")
            return False
        toExecute += list(
            map(lambda x: parsedCode["codelines"][x], parsedCode["patternAufgabe"])
        )
        if len(parsedCode["patternStudentenLD"]) == 0:
            if not quiet:
                raise AssertionError("Studentenliste ist nicht definiert!")
            return False
        toExecute += list(
            map(lambda x: parsedCode["codelines"][x], parsedCode["patternStudentenLD"])
        )
        if len(parsedCode["patternStudentenAP"]) == 0:
            if not quiet:
                raise AssertionError("Es wurden keine Studenten eingetragen!")
            return False
        toExecute += list(
            map(lambda x: parsedCode["codelines"][x], parsedCode["patternStudentenAP"])
        )
        toExecute += "\nfrom Grading.Grading import *\n"
        toExecute += (
            "Grading.CheckStudents(Studenten, Gruppennummer, Aufgabe,printList=%s)\n"
            % (str(not quiet))
        )
        try:
            G = {}  # Globaler Scope fuer die Ausfuehrung
            exec("".join(toExecute), G)
        except Exception as e:
            if not quiet:
                raise AssertionError(e)
            return False
        # Alle Tests bestanden
        return True
