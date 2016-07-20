UPDATE fennec_release SET status='shipped' WHERE status IN ('postrelease', 'Post Release');
UPDATE firefox_release SET status='shipped' WHERE status IN ('postrelease', 'Post Release');
UPDATE thunderbird_release SET status='shipped' WHERE status IN ('postrelease', 'Post Release');
