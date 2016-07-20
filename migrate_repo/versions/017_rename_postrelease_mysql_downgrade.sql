UPDATE fennec_release SET status='postrelease' WHERE status='shipped';
UPDATE firefox_release SET status='postrelease' WHERE status='shipped';
UPDATE thunderbird_release SET status='postrelease' WHERE status='shipped';
