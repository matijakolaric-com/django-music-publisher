# Code audit — 11 groups

Full-tree scan of `music_publisher/` and `dmp_project/` on `master` @ `0f598cb`
(post-26.9). Items marked **[verified]** were reproduced by executing code, not
just read. Others are read from the source and are marked as such.

---

## Group 1 — Authorization holes

### 1.1 `admin.py:2209-2258` — `CWRExportAdmin.change_view` sub-views bypass permission checks **[verified]**

The override fetches the object and serves `?preview`, `?download`, `?create_cwr`
before `_changeform_view` reaches `has_view_or_change_permission`
(`django/contrib/admin/options.py:1866-1869`). Reproduced with a staff account
holding **zero** model permissions:

```
cwr download: HTTP 200     <- full CWR file
cwr create:  HTTP 302     <- obj.create_cwr() actually ran, wrote to DB
ack preview: HTTP 200
plain change: HTTP 403     <- correct behaviour, for contrast
```

`?create_cwr=true` is a state change reachable by GET from any staff account.

### 1.2 `admin.py:2586-2631` — same pattern in `ACKImportAdmin.change_view` **[verified]**

`?preview=true` serves the stored CWR acknowledgement to the same unprivileged
staff account (HTTP 200 above).

### 1.3 `royalty_calculation.py:457-461` — `@csrf_exempt` on `dispatch` **[verified]**

`POST` with no CSRF token passed straight through to form processing instead of
returning 403. The template still renders `{% csrf_token %}`, so the exemption
buys nothing.

### 1.4 `admin.py:2175-2181` — `has_change_permission` returns the *delete* permission **[verified]**

```python
def has_change_permission(self, request, obj=None):
    """If object exists, it can only be edited in changelist."""
    if not settings.PUBLISHER_CODE:
        return False
    if obj:
        return False
    return super().has_delete_permission(request, obj)
```

The changelist calls this with `obj=None`
(`django/contrib/admin/views/main.py:149`), and `list_editable = ("description",)`
is set at `admin.py:2129`. Measured on the CWR exports changelist:

| permissions | inline `description` editor |
|---|---|
| `change_cwrexport` only | **not rendered** |
| `delete_cwrexport` only | **rendered** |
| both | rendered |
| `view_cwrexport` only | not rendered |

History: correct from `096c83a` (2018-07-26, released 18.7), changed to the delete
variant in `41a503f` (2020-05-16, first released in 20.7a1), carried through
`04ce04a` and never restored.

---

## Group 2 — Stored XSS

### 2.1 `admin.py:2291-2293` sink, `2504-2507` + `2517-2521` source **[verified]**

`AdminWithReport.print_report` returns `mark_safe(obj.report)`. `_import_iswc`
builds that report with `.format(work, ...)`, and `Work.__str__` embeds
`self.title.upper()` (`models.py:801-804`). Verified end to end with a work titled
`<img src=x onerror=alert(1)>`:

```
str(work): 123000001: <IMG SRC=X ONERROR=ALERT(1)> ()
report contains raw tag: True
print_report() output contains raw tag: True
```

Uppercasing does not help — HTML tag names are case-insensitive. Reachable by
importing a CWR acknowledgement whose work title carries the payload; fires for
whoever opens that import's change page. `_process_ack_record` (`:2468`) does the
same job correctly with `format_html`; only `_import_iswc` does not.

---

## Group 3 — Business rules silently skipped

### 3.1 `data_import.py:482-484` — the per-writer formset validation is a no-op **[verified]**

```python
form.initial = form.cleaned_data = data
form.full_clean()     # is_bound is still False -> returns immediately
form.is_bound = True  # too late; formset.clean()'s result is never read
formset.clean()
```

Two distinct checks are dead — `forms.py:208` (`"Not allowed in original works."`)
and `forms.py:219` (`check_extended_capacity`). Verified:

```
ORIGINAL work, writer role AD: IMPORTED -> [('AD', True), ('C ', True)]   <- should be rejected
MODIFIED work, writer role C : IMPORTED -> [('C ', True), ('C ', True)]   <- should be rejected
```

A CSV can therefore create original works with Adaptor/Arranger writers, and
modified works with none.

### 3.2 `data_import.py:366-368` — `LibraryRelease` is the only object saved unvalidated **[verified]**

Every other object gets `clean_fields()` + `clean()` first. Reproduced:

```
same CD identifier under a different library
  -> IntegrityError: UNIQUE constraint failed: music_publisher_release.cd_identifier
```

The lookup keys on `library_id` + `cd_identifier` (`:362-365`) but
`cd_identifier` is `unique=True` on the shared `Release` table (`base.py:414`),
so a legal-looking second library misses the lookup and then hits an unhandled
`IntegrityError` that aborts the whole import — unlike the
`IntegrityError` → `ValidationError` handling at `:408-417`. `cd_identifier`
also escapes `max_length=15` and `CWRFieldValidator("name")` (`base.py:409-416`).

### 3.3 `base.py:253-257` — `_can_be_controlled` computed before the placeholders are nulled

```python
self._can_be_controlled = bool(self.ipi_name) & bool(self.pr_society)
if self.ipi_name == "00000000000": self.ipi_name = None
if self.pr_society == "99": self.pr_society = None
```

Both `"00000000000"` (produced by `IPIBase.clean_fields`, `base.py:203`) and
`"99"` are truthy, so a writer lands generally-controlled with both fields `None`,
and exports to CWR with no PR affiliation.

### 3.4 `base.py:193-195`, `253` — `_can_be_controlled` only assigned in `clean()`

`Model.save()` does not call `clean()`, so `Writer.objects.create(...)` keeps the
column default `False`. `WriterInWork._controlled_writer_errors`
(`models.py:1157`) then rejects a legitimate controlled writer with *"IPI name and
PR society must be set"* for fields that *are* set, and the `list_filter`
(`admin.py:881`) misreports such writers.

### 3.5 `models.py:450-454` — `Playlist.cd_identifier` generated in `clean()`

`Playlist.objects.create(...)` writes `NULL`; `PlaylistManager` filters on
`cd_identifier__isnull=False` (`models.py:284-286`), so the row immediately fails
`Playlist.objects.get(pk=...)` and surfaces as a `CommercialRelease`.

### 3.6 `models.py:2230-2237` — `description` written past `max_length`

`CWRExport.description` is `max_length=60` (`models.py:1585`) but
`create_cwr_files` writes `"{description} ({number})"` via `objects.create()`,
which skips `full_clean()`. Same class of bug as the data-import file name
fixed in `0f598cb`.

---

## Group 4 — Unhandled exceptions on bad input (500s)

### 4.1 `royalty_calculation.py:126-127` — `TextIOWrapper` outside the `try` **[verified]**

`POST` with no file → `AttributeError: 'NoneType' object has no attribute
'readable'` → 500.

### 4.2 `royalty_calculation.py:345-348` — wrong exception class around `Decimal()` **[verified]**

```python
try:
    amount = Decimal(row[self.ac])
except TypeError:
    amount = None
```

`Decimal("")` / `Decimal("abc")` / `Decimal("1,000.00")` raise
`decimal.InvalidOperation`, never `TypeError`. One empty amount cell in a valid
statement is a 500.

### 4.3 `royalty_calculation.py:337-342`, `:344` — unguarded dict lookup

`{"p": …, "m": …, "s": …}[right]` with right-type `Z` → `KeyError`.

### 4.4 `royalty_calculation.py:337` — empty right-type cell misreported

`row[self.rc][0]` on `""` raises `IndexError`, caught at `:350`, which returns
`(None, None, None)` and **discards the already-resolved work**: the output row
reads `ERROR: Work not found` for a work that exists. A wrong answer in a
financial report, not a crash.

### 4.5 `data_import.py:374` — `row.values()` contains `None` **[verified]**

A short CSV row gives `AttributeError: 'NoneType' object has no attribute 'strip'`,
surfaced to the user as that raw message. `unflatten` guards this at `:180`; this
line does not.

### 4.6 `models.py:2120-2127` and `admin.py:1637-1640` — nullable `library` subscripted

`work["origin"]["library"]["name"]` / `origin["library"]["name"]` on a value
`get_origin_dict` explicitly documents as nullable (`models.py:355-358`).
`Release.__str__` renders the same state as the literal `"None"`
(`models.py:198-207`, verified: `'CD9: X (None)'`).

### 4.7 `models.py:904-907` — proxy/concrete confusion

The FK targets the `LibraryRelease` proxy but Django type-checks against the
concrete model, so `Work(library_release=Release(...))` caches a `Release`, which
has no `get_origin_dict` → `AttributeError`. The repo's own test does this
(`tests.py:315`, `tests.py:591`) and escapes only because it calls
`refresh_from_db()` first.

### 4.8 `data_import.py:120-124` — unreachable `key.upper()`

`re.match(r"^([0-9]+|[A-Z]+)", value)` matches only uppercase, so
`"c – Composer"` raises `ValueError: Bad value` at `:122` before `key.upper()` is
reached.

---

## Group 5 — Wrong values in generated CWR files

### 5.1 `cwr_templates.py:422` — 3.x ISR renders `{{ work_id }}`, a key never produced **[verified]**

`Work.get_dict()` has `code`, not `work_id`
(verified: `{'code': '123000001'}`). The 2.x `WRK` template correctly uses
`{{ code|ljust:14 }}` for the same 14-char field. Rendered 3.x ISR:

```
ISR0000000100000000MUSIC PUB CARTOONS <14 spaces> T1234567891U
```

The work ID is blank **structurally**, even for works that have one. The golden
fixture `tests/CW220003DMP_0000_V3-0-0.ISR` has the blank baked in, which is why
the suite passes.

### 5.2 `cwr_templates.py:430` — 3.x WRI renders `{{ capacity }}`

`WriterInWorkDict` keys are
`['controlled', 'original_publishers', 'relative_share', 'writer', 'writer_role']`
(verified); the sibling `SWR` record correctly uses `writer_role`. Same shape as
5.1. **Whether blank is correct per the CWR 3.x spec is unconfirmed** — the
fixture has it blank too, so this needs a spec check, not just a code fix.

### 5.3 `cwr_templates.py:323-325` — OWT writes `pr_share` in the SR slot

SPT/SWT/OPT all render `sr_share` in the third slot. Currently masked because
`yield_other_writer_lines` (`models.py:1966-1970`) forces all three equal for OWT,
but any non-equal PR/SR share produces a wrong SR share.

### 5.4 `cwr_templates.py:460-464` — 3.1 `GRH` hardcodes `WRK`

`TEMPLATES_30["GRH"]` renders `{{ transaction_type|ljust:3 }}`; the 3.1 copy does
not. Latent behind 5.6.

### 5.5 `admin.py:2241` — latin1 round trip corrupts non-ASCII

`obj.cwr.encode().decode("latin1")` re-decodes UTF-8 bytes as latin1, so every
accented character in a CWR download is mojibake. A no-op only for pure ASCII.

### 5.6 `models.py:2168` — only `ISR` is special-cased

`yield_lines` special-cases `"ISR"` but not `"IS1"`, so a 3.1 ISWC request emits
WRK records into a `.SUB` file.

---

## Group 6 — Configuration read wrongly

### 6.1 `settings.py:18` — `DEBUG = os.getenv("DEBUG", False)` **[verified]**

`DEBUG=false` yields the truthy string `"false"`, enabling debug mode, the
toolbar, and tracebacks leaking the settings dict (DB password, `SECRET_KEY`) to
anonymous callers — while also turning *off* `CSRF_COOKIE_SECURE`,
`SESSION_COOKIE_SECURE` and HSTS (`:130-133`).

### 6.2 `settings.py:226`, `:187` — same defect

`OPTION_FILES` and `OPTION_CWR_NO_GENERATE_LINK` read env strings the same way.
`OPTION_FILES=false` still takes the `if OPTION_FILES:` branch.

### 6.3 `api.py:330` — `Cache-Control` set to a tuple **[verified]**

`response["Cache-Control"] = ("no-cache",)` emits the literal header
`Cache-Control: ('no-cache',)`, an invalid directive, so the intended no-cache on
the full-catalogue backup does not apply.

### 6.4 `royalty_calculation.py:90-93` — form default read at import time

`initial=settings.PUBLISHER_CODE` is evaluated in the class body, so unlike the
agreement shares (`:339-341`) it cannot be overridden. With the code unset,
`initial` is `None` while `get_id_sources` offers `(None, …)` — a choice
`ChoiceField.valid_value` rejects, so the default is unselectable.

---

## Group 7 — Resource leaks and unbounded input

### 7.1 `royalty_calculation.py:424-435` — temp file and fd leaked on every error

The `try/finally` starts *after* the write loop, so any `process_row` exception
leaves the `delete=False` temp file on disk with the handle open, and
`form_valid`'s `os.remove` (`:471`) is never reached.

### 7.2 `royalty_calculation.py:460` + `settings.py:128` — no upload size cap

Replacing `request.upload_handlers` with a bare `TemporaryFileUploadHandler` means
`FILE_UPLOAD_MAX_MEMORY_SIZE` never applies and nothing caps the body;
`DATA_UPLOAD_MAX_NUMBER_FIELDS = None` removes the admin's field-count guard too.
Processing runs in the request-response cycle, so one account with
`can_process_royalties` can exhaust disk and CPU.

---

## Group 8 — Arithmetic and validation edge cases

### 8.1 `royalty_calculation.py:320`, `:366` — division by zero

`controlled = sum(...) / 100` then `owned_share / controlled`. `relative_share`
only has `MinValueValidator(0)` (`models.py:1088-1093`) and `check_total`
(`:241-242`) checks the all-writer total, never that a controlled one is
non-zero. A work with one controlled writer at `0.00` and uncontrolled writers
carrying the 100% is valid through the admin → `DivisionUndefined`.

### 8.2 `validators.py:172-175` — `isnumeric()` accepts non-ASCII numerics

`"400638133393①"` passes both the `isnumeric()` and length checks, then
`check_ean_digit` executes `int("①")` → `ValueError`, escaping as a 500 instead of
a field error on `Release.ean`.

---

## Group 9 — Concurrency

### 9.1 `models.py:2291-2308` — `create_cwr()` races on the stop marker and `num_in_year`

Both the guard and the sequence number are read-then-write with no transaction
and no `select_for_update`. Two processes (a web request saving a small export
via `admin.py:2255` while `manage.py generatecwr` runs) can both read `stop` as
absent and both compute the same `num_in_year`, leaving two exports in one year
with the same delivery filename (`models.py:1616-1653`) and one CWR body silently
discarded.

Not reproducible on demand — read from the code.

---

## Group 10 — Performance

### 10.1 `models.py:313`, `:386`, `:429` — severe N+1 in `*ReleaseManager.get_dict`

`Release.get_dict` → `track.get_dict` → `recording.get_dict(with_work=True)` →
`work.get_dict`, none with `select_related`/`prefetch_related`, and `track.release`
is not cached. Measured 41 queries for 4 releases × 1 track. This is the admin
`create_json` action (`admin.py:636`, `:843`) and the backup endpoint
(`api.py:321`).

### 10.2 `admin.py:1132`, `:1143` — COUNT per row in `list_display`

`WorkAdmin.get_queryset` (`:1162-1168`) prefetches only three relations, and
`.count()` never uses the prefetch cache, so the work changelist runs two extra
COUNTs per displayed row.

---

## Group 11 — Broken links, filters and admin plumbing

### 11.1 `admin.py:621-622`, `:827-828`, `:749-750` — `track_count` links to a nonexistent filter **[verified]**

`Recording` has `releases` (M2M), no `release` field. `lookup_allowed` silently
skips the unknown part, so the link renders on the changelist (confirmed present
in the HTML) but clicking it redirects to `?e=1` — the admin "invalid filter"
page. Affects three changelists.

### 11.2 `admin.py:1400-1402` — work ID search ignores the parsed `0*`

```python
match = re.match(r"^([A-Za-z]+)0*(\d+)$", term)
if match:
    return queryset.filter(_work_id__iexact=term), False
```

`_work_id` is always stored zero-padded (`models.py:761-764`), so `MK123` matches
nothing while `MK000123` works — despite the docstring naming `"X123"` as a
supported shape. The numeric branch below does normalize.

### 11.3 `admin.py:1434-1441` — `save_formset` passes the wrong parent object

The loop variable `form` shadows the `form` parameter, so
`super().save_formset(request, form, formset, change)` receives the last inline
form instead of the parent `WorkForm`. Currently inert (Django ignores the
argument) but wrong.

### 11.4 `forms.py:256` — `DataImportForm.Meta.model = ACKImport`

The form is bound to `DataImport` (`admin.py:2643`). `_post_clean` validates a
throwaway `ACKImport`; any `form.save()` would insert an empty `ACKImport` row.

### 11.5 `models.py:175-176` — `Release` loses `ReleaseBase.Meta` wholesale **[verified]**

`ReleaseBase.ordering` is `('release_title', 'cd_identifier', '-id')`;
`Release.ordering` and all three proxies are `[]`. `Release.objects.all()`
(the backup endpoint, `api.py:318`) returns arbitrary order.

---

## Fixed in post-26.9 work

`0f598cb` — data import with an over-long file name now rejected at the form
layer, with a readable message and no spurious second error.
