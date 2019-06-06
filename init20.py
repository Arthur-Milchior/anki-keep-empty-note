# From: https://github.com/Arthur-Milchior/anki-keep-empty-note
# Modified by lovac42 for Anki 2.0.52
# Only this file is required.


from aqt.main import *
from anki.lang import _
from aqt import mw, dialogs


cids=None
def onEmptyCards(self):
        """Method called by Tools>Empty Cards..."""
        global cids
        self.progress.start(immediate=True)
        # print("Calling new onEmptyCards")

        cids = self.col.emptyCids()
        if not cids:
            self.progress.finish()
            tooltip(_("No empty cards."))
            return
        # print("Calling emptyCardReport from new onEmptyCards with cids %s"%cids)


        report = self.col.emptyCardReport(cids)
        self.progress.finish()
        part1 = ngettext("%d card", "%d cards", len(cids)) % len(cids)
        part1 = _("%s to delete:") % part1
        diag, box = showText(part1 + "\n\n" + report, run=False,
                geomKey="emptyCards")
        box.addButton(_("Delete Cards"), QDialogButtonBox.AcceptRole)
        box.button(QDialogButtonBox.Close).setDefault(True)

        def onDelete():
            global cids
            cids=set(cids)  #change here to make a set


            saveGeom(diag, "emptyCards")
            QDialog.accept(diag)
            self.checkpoint(_("Delete Empty"))

            # Beginning of changes
            nidToCidsToDelete = dict()
            for cid in cids:
                card = self.col.getCard(cid)
                nid = card.note().id
                if nid not in nidToCidsToDelete:
                    # print("note %s not yet in nidToCidsToDelete. Thus adding it"%nid)
                    nidToCidsToDelete[nid] = 0
                # else:
                    # print("note %s already in nidToCidsToDelete."%nid)
                nidToCidsToDelete[nid]+=1
                # print("Adding card %s to note %s."%(cid,nid))

            emptyNids = 0
            for nid in nidToCidsToDelete:
                note = self.col.getNote(nid)
                cidsOfNids =  len ( note.cards() )

                if cidsOfNids <= nidToCidsToDelete[nid]:
                    emptyNids+=1
                    note.addTag("NoteWithNoCard")
                    note.flush()
                    cids -= set([note.cards()[0].id]) #keep one card
                # else
                    # cloze type or normal delete
                    # unlike note types, cloze types are never totally removed.


            self.col.remCards(cids, notes = False)
            nidsWithTag = set(self.col.findNotes("tag:NoteWithNoCard"))
            # print("emptyNids is %s, nidsWithTag is %s"%(emptyNids,nidsWithTag))

            if emptyNids:
                showWarning("""%d note(s) should have been deleted because they had no more cards. They now have the tag "NoteWithNoCard". Please go check them. Then either edit them to save their content, or delete them from the browser."""%emptyNids)
                browser = dialogs.open("Browser", mw)
                browser.form.searchEdit.lineEdit().setText("tag:NoteWithNoCard")

            # end of changes
            tooltip(ngettext("%d card deleted.", "%d cards deleted.", len(cids)) % len(cids))
            self.reset()

        box.accepted.connect(onDelete)
        diag.show()



AnkiQt.onEmptyCards = onEmptyCards
mw.form.actionEmptyCards.triggered.disconnect()
mw.form.actionEmptyCards.triggered.connect(mw.onEmptyCards)
