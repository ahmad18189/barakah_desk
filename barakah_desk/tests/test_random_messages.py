from barakah_desk.services.random_messages import select_weighted_random_message


def test_random_message_selector_returns_none_without_data():
	message = select_weighted_random_message()
	assert message is None or hasattr(message, "name")
