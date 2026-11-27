---- MODULE HudNote ----
\* One problem in a session, one observer note about it, in panel mode.
EXTENDS Naturals
CONSTANT RECHECK

VARIABLES fact, note, moved, seen, shownStale, sends, looked
vars == <<fact, note, moved, seen, shownStale, sends, looked>>

Init == /\ fact = "open" /\ note = "none" /\ moved = FALSE /\ seen = "open"
        /\ shownStale = FALSE /\ sends = 0 /\ looked = FALSE

\* The agent fixes the problem, at any moment.
AgentSettles == /\ fact = "open" /\ fact' = "settled" /\ moved' = TRUE
                /\ UNCHANGED <<note, seen, shownStale, sends, looked>>

\* The agent does other work that leaves the problem as it was.
AgentWorks == /\ note \in {"looking", "rechecking"} /\ ~moved /\ moved' = TRUE
              /\ UNCHANGED <<fact, note, seen, shownStale, sends, looked>>

\* The observer reads the session; the HUD never raises one problem twice.
ObserverLooks == /\ note = "none" /\ fact = "open" /\ ~looked
                 /\ note' = "looking" /\ moved' = FALSE /\ looked' = TRUE /\ seen' = fact
                 /\ UNCHANGED <<fact, shownStale, sends>>

Show == /\ note' = "shown" /\ shownStale' = (fact = "settled")

\* The reply drafts a note. With no later turns, or no recheck, it is shown at once.
ReplyQuiet == /\ note = "looking" /\ (~RECHECK \/ ~moved) /\ Show
              /\ UNCHANGED <<fact, moved, seen, sends, looked>>
\* Later turns arrived while the observer worked: read them again before showing.
ReplyMoved == /\ RECHECK /\ note \in {"looking", "rechecking"} /\ moved
              /\ note' = "rechecking" /\ seen' = fact /\ moved' = FALSE
              /\ UNCHANGED <<fact, shownStale, sends, looked>>
RecheckSettled == /\ note = "rechecking" /\ seen = "settled" /\ note' = "dropped"
                  /\ UNCHANGED <<fact, moved, seen, shownStale, sends, looked>>
RecheckHolds == /\ note = "rechecking" /\ seen = "open" /\ ~moved /\ Show
                /\ UNCHANGED <<fact, moved, seen, sends, looked>>

PersonOpens == /\ note = "shown" /\ note' = "read" /\ UNCHANGED <<fact, moved, seen, shownStale, sends, looked>>
PersonSends == /\ note \in {"shown", "read"} /\ note' = "sent" /\ sends' = sends + 1
               /\ UNCHANGED <<fact, moved, seen, shownStale, looked>>
PersonMarks == /\ note \in {"shown", "read"} /\ note' = "closed"
               /\ UNCHANGED <<fact, moved, seen, shownStale, sends, looked>>

Done == /\ (note \in {"sent", "closed", "dropped"} \/ (note = "none" /\ fact = "settled"))
        /\ UNCHANGED vars

Next == AgentSettles \/ AgentWorks \/ ObserverLooks \/ ReplyQuiet \/ ReplyMoved \/ RecheckSettled \/ RecheckHolds
        \/ PersonOpens \/ PersonSends \/ PersonMarks \/ Done

\* Rules the person agreed to.
NoStaleNote == ~shownStale                           \* a note is never shown after the agent already fixed it
SentOnce == sends <= 1                               \* one note reaches the agent at most once
DropOnlyFixed == note = "dropped" => fact = "settled" \* a dropped note was really settled
====
