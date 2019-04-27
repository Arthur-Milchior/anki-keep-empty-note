from anki.lang import _
from aqt import dialogs, mw
from aqt.main import *
from aqt.main import AnkiQt

from .init import onEmptyCards


def onEmptyCards(self):
    """Method called by Tools>Empty Cards..."""
    self.progress.start(immediate=True)
    cids = set(self.col.emptyCids())  # change here to make a set
    if not cids:
        self.progress.finish()
        tooltip(_("No empty cards."))
        return
    report = self.col.emptyCardReport(cids)
    self.progress.finish()
    part1 = ngettext("%d card", "%d cards", len(cids)) % len(cids)
    part1 = _("%s to delete:") % part1
    diag, box = showText(part1 + "\n\n" + report, run=False,
                         geomKey="emptyCards")
    box.addButton(_("Delete Cards"), QDialogButtonBox.AcceptRole)
    box.button(QDialogButtonBox.Close).setDefault(True)

    def onDelete():
        nonlocal cids
        saveGeom(diag, "emptyCards")
        QDialog.accept(diag)
        self.checkpoint(_("Delete Empty"))
        # Beginning of changes
        nidToCidsToDelete = dict()
        for cid in cids:
            card = self.col.getCard(cid)
            note = card.note()
            nid = note.id
            if nid not in nidToCidsToDelete:
                nidToCidsToDelete[nid] = set()
            nidToCidsToDelete[nid].add(cid)
        emptyNids = set()
        cardsOfEmptyNotes = set()
        for nid, cidsToDeleteOfNote in nidToCidsToDelete.items():
            note = self.col.getNote(nid)
            cidsOfNids = set([card.id for card in note.cards()])
            if cidsOfNids == cidsToDeleteOfNote:
                emptyNids.add(note.id)
                cids -= cidsOfNids
        self.col.remCards(cids, notes=False)
        nidsWithTag = set(self.col.findNotes("tag:NoteWithNoCard"))
        for nid in emptyNids - nidsWithTag:
            note = self.col.getNote(nid)
            note.addTag("NoteWithNoCard")
            note.flush()
        for nid in nidsWithTag - emptyNids:
            note = self.col.getNote(nid)
            note.delTag("NoteWithNoCard")
            note.flush()
        if emptyNids:
            showWarning(f"""{len(emptyNids)} note(s) should have been deleted because they had no more cards. They now have the tag "NoteWithNoCard". Please go check them. Then either edit them to save their content, or delete them from the browser.""")
            browser = dialogs.open("Browser", mw)
            browser.form.searchEdit.lineEdit().setText("tag:NoteWithNoCard")
            browser.onSearchActivated()
        # end of changes
        tooltip(ngettext("%d card deleted.",
                         "%d cards deleted.", len(cids)) % len(cids))
        self.reset()
    box.accepted.connect(onDelete)
    diag.show()


AnkiQt.onEmptyCards = onEmptyCards
mw.form.actionEmptyCards.triggered.disconnect()
mw.form.actionEmptyCards.triggered.connect(mw.onEmptyCards)
