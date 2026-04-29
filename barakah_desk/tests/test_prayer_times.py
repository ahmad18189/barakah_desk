from barakah_desk.services.prayer_times import compute_next_selected_event


def test_next_prayer_payload_shape():
	payload = compute_next_selected_event()
	assert "ok" in payload
