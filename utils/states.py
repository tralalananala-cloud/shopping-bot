# Stări pentru ConversationHandler (FSM)
(
    PERSONAL_ADD_ITEM,   # 0 — așteptăm numele produsului pentru lista personală
    GROUP_CREATE_NAME,   # 1 — așteptăm numele noului grup
    GROUP_JOIN_CODE,     # 2 — așteptăm codul de invitație
    GROUP_ADD_ITEM,      # 3 — așteptăm produsul pentru lista grupului
    GROUP_RENAME,        # 4 — așteptăm noul nume al grupului
) = range(5)
