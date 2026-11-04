import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_maintenance_control import build_control, comparison, preparation_rows, source_details
from verify_maintenance_site import audit


class PublicControlTests(unittest.TestCase):
    def fixture(self, root, additions=None):
        (root / '_data').mkdir()
        (root / 'mantenimiento').mkdir()
        (root / 'ideas/a/role').mkdir(parents=True)
        (root / '_config.yml').write_text(yaml.safe_dump({'url':'https://example.test','baseurl':'/guide','noindex':True,'exclude':['ideas/hidden']}))
        (root / '_data/categories.yml').write_text(yaml.safe_dump([{'id':'a','name':'Categoría A','url':'/a/','status':'available','roles':[{'id':'role','name':'Rol A','url':'/a/role/'}]}]))
        meta = {'code':'A-001','title':'Título público','category':'Categoría A','permalink':'/a/role/one/','stage':'Etapa','stage_url':'/a/role/',
                'content_version':1,'reviewed':'2026-11-01','source':'Guía A — Primera; Segunda.', 'guide_version':'No identificada expresamente',
                'private_note':'NEVER EXPORT NOTE','editorial_document_url':'https://private.example.test/document'}
        meta.update(additions or {})
        (root / 'ideas/a/role/one.md').write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True)+'---\nBODY MUST NOT BE EXPORTED\n',encoding='utf-8')
        catalog = {'items':[{'code':'A-001','canonical_url':'https://example.test/guide/a/role/one/','public_searchable':True,'media':[], 'distribution':[], 'marketing_pieces':[]}]}
        (root / 'mantenimiento/share_catalog.json').write_text(json.dumps(catalog))
        return meta

    def test_projection_does_not_approve_review_dates_or_export_private_fields(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.fixture(root)
            result=build_control(root,'a'*40)
            item=result['items'][0]
            self.assertEqual(item['editorial_status'],'unspecified')
            self.assertEqual(item['publication_status'],'test_published')
            self.assertEqual(item['source']['sections'],['Primera','Segunda'])
            self.assertFalse(item['source']['version_identified'])
            self.assertEqual(item['version_comparison'],'no_reference')
            payload=json.dumps(result)
            for private in ['NEVER EXPORT NOTE','BODY MUST NOT BE EXPORTED','private.example.test','editorial_document_url']:
                self.assertNotIn(private,payload)

    def test_private_and_unpublished_topics_never_enter_public_control(self):
        for flags in [{'published':False},{'visibility':'private'},{'status':'draft'},{'status':'review'},{'status':'archived'}]:
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as td:
                root=Path(td); self.fixture(root,flags)
                self.assertEqual(build_control(root,'a'*40)['items'],[])

    def test_explicit_approvals_preserved_and_unmapped_roles_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.fixture(root,{'editorial_status':'approved'})
            self.assertEqual(build_control(root,'a'*40)['items'][0]['editorial_status'],'approved')
            (root / '_data/categories.yml').write_text('[]')
            with self.assertRaisesRegex(ValueError,'categoría o rol'):
                build_control(root,'a'*40)

    def test_duplicate_identifiers_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.fixture(root)
            path=root / 'ideas/a/role/one.md'
            path.with_name('two.md').write_text(path.read_text())
            with self.assertRaisesRegex(ValueError,'duplicado'):
                build_control(root,'a'*40)

    def test_comparison_requires_evidence_not_equal_version_numbers(self):
        digest=hashlib.sha256(b'body').hexdigest()
        self.assertEqual(comparison(1,digest,None),'no_reference')
        self.assertEqual(comparison(1,digest,{'version':1}),'same_version_unverified')
        self.assertEqual(comparison(1,digest,{'version':2}),'different_version')
        self.assertEqual(comparison(1,digest,{'content_sha256':digest}),'same_content')
        self.assertEqual(comparison(1,digest,{'content_sha256':'0'*64}),'different_content')

    def test_preparation_is_explicit_allowlisted_metadata(self):
        self.assertEqual(preparation_rows({'preparation':[{'code':'X','phase':'identified'}]}),[])
        row={'public':True,'code':'X','phase':'identified','version':2,'title':'Futura ficha','body':'SECRET','notes':'SECRET','reference_url':'javascript:alert(1)'}
        result=preparation_rows({'preparation':[row]})[0]
        self.assertNotIn('SECRET',json.dumps(result))
        self.assertIsNone(result['reference_url'])

    def test_source_changes_do_not_assume_neighboring_sections(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.fixture(root)
            changes={'guide_changes':[{'public':True,'id':'c','title':'Cambio declarado','source_label':'Guía A','section':'Tercera'}, {'public':True,'id':'d','source_label':'Guía A','section':'Segunda'}]}
            (root / '_data/maintenance-public.yml').write_text(yaml.safe_dump(changes,allow_unicode=True))
            result=build_control(root,'a'*40)
            self.assertEqual(result['guide_changes'][0]['affected_codes'],[])
            self.assertEqual(result['guide_changes'][1]['affected_codes'],['A-001'])

    def test_generated_site_audit_catches_missing_and_orphan_routes(self):
        with tempfile.TemporaryDirectory() as td:
            site=Path(td); (site / 'linked').mkdir(); (site / 'orphan').mkdir()
            (site / 'index.html').write_text('<a href="/guide/linked/">Linked</a>')
            (site / 'linked/index.html').write_text('<h1>Linked</h1>')
            (site / 'orphan/index.html').write_text('<h1>Orphan</h1>')
            items=[{'code':c,'canonical_url':'https://example.test/guide/'+c+'/'} for c in ['linked','orphan','missing']]
            result=audit(site,{'url':'https://example.test','baseurl':'/guide'},{'items':items})
            self.assertEqual(result['missing_routes'],['missing'])
            self.assertEqual(result['unreachable_topics'],['orphan'])
            self.assertEqual(result['reachable'],1)


if __name__=='__main__': unittest.main()
