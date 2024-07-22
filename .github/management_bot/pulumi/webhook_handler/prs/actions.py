def add_label():
    if not msg_len == 2:
        send_error(
            selected_obj,
            sender=SENDER["login"],
            body=COMMENT["body"],
            msg_len=msg_len,
            required=2,
            example_cmd="add_label bug",
        )

        return g.close()

    selected_obj.add_to_labels(msg_stripped[1])
    selected_obj.create_comment(f"Okay @{SENDER['login']}, I have added the label '{msg_stripped[1]}'")
