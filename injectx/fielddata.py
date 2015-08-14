"""XBlock.field_data support for injections.

Use this patch:

    git apply injector.patch

---8<--  injector.patch ----------------8<-------------
diff --git a/lms/djangoapps/courseware/module_render.py b/lms/djangoapps/courseware/module_render.py
index 52f338b..b7def08 100644
--- a/lms/djangoapps/courseware/module_render.py
+++ b/lms/djangoapps/courseware/module_render.py
@@ -749,12 +749,15 @@ def get_module_for_descriptor_internal(user, descriptor, student_data, course_id
         course=course
     )

+    from injectx.fielddata import FieldDataInjector
+
     descriptor.bind_for_student(
         system,
         user.id,
         [
             partial(OverrideFieldData.wrap, user, course),
             partial(LmsFieldData, student_data=student_data),
+            FieldDataInjector,
         ],
     )

-------------------------------------------------------
"""

from xblock.field_data import FieldData

from injectx.injector import Injector


class FieldDataInjector(FieldData):

    INJECTOR = Injector(
        hints={
            'SequenceDescriptor.start': { 'type': 'date' },
            'SequenceDescriptor.due': { 'type': 'date' },
            'CourseDescriptor.start': { 'type': 'date' },
            'CourseDescriptor.due': { 'type': 'date' },

            'CourseInfoModule.data': { 'type': 'html' },
            'HtmlModule.data': { 'type': 'html' },

            'SequenceDescriptor.format': { 'knownbad': True },

            'VideoModule.youtube_id_1_0':  { 'knownbad': True },
            'VideoModule.youtube_id_1_25':  { 'knownbad': True },
            'VideoModule.youtube_id_1_5':  { 'knownbad': True },
        },
    )

    def __init__(self, field_data):
        self.field_data = field_data

    def get(self, block, name):
        val = self.field_data.get(block, name)
        class_name = block.__class__.__name__
        if class_name.endswith("WithMixins"):
            class_name = class_name[:-len("WithMixins")]
        name = class_name + "." + name
        val = self.INJECTOR.munge(name, val)
        return val

    def has(self, block, name):
        return self.field_data.has(block, name)

    def set(self, block, name, value):
        return self.field_data.set(block, name, value)

    def delete(self, block, name):
        return self.field_data.delete(block, name)
